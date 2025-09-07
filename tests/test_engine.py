import pytest
from laissez_faire.engine import GameEngine
from laissez_faire.llm import LLMProvider
import os
import json
from unittest.mock import MagicMock

@pytest.fixture
def mock_llm_providers():
    """Fixture for a mock LLM providers dictionary."""
    return {"player1": MagicMock(spec=LLMProvider)}

@pytest.fixture
def mock_scorer_llm_provider():
    """Fixture for a mock scorer LLM provider."""
    return MagicMock(spec=LLMProvider)

def test_load_scenario_success(mock_llm_providers, mock_scorer_llm_provider):
    """
    Tests that a scenario is loaded correctly.
    """
    # Create a dummy scenario file
    scenario_content = '{"name": "Test Scenario", "start_date": "2024-01-01"}'
    scenario_path = "test_scenario.json"
    with open(scenario_path, "w") as f:
        f.write(scenario_content)

    engine = GameEngine(scenario_path, llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider)
    assert engine.scenario["name"] == "Test Scenario"
    assert engine.scenario["start_date"] == "2024-01-01"

    # Clean up the dummy file
    os.remove(scenario_path)

def test_load_scenario_file_not_found(mock_llm_providers, mock_scorer_llm_provider):
    """
    Tests that a FileNotFoundError is raised when the scenario file does not exist.
    """
    with pytest.raises(FileNotFoundError):
        GameEngine("non_existent_scenario.json", llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider)

def test_load_scenario_invalid_json(mock_llm_providers, mock_scorer_llm_provider):
    """
    Tests that an error is raised when the scenario file is not valid JSON.
    """
    # Create a dummy invalid scenario file
    scenario_content = '{"name": "Test Scenario", "start_date": "2024-01-01"'
    scenario_path = "invalid_scenario.json"
    with open(scenario_path, "w") as f:
        f.write(scenario_content)

    with pytest.raises(json.JSONDecodeError):
        GameEngine(scenario_path, llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider)

    # Clean up the dummy file
    os.remove(scenario_path)


def test_game_engine_run_and_turn_increment(mock_llm_providers, mock_scorer_llm_provider):
    """
    Tests that the game engine's run method executes and increments the turn.
    """
    engine = GameEngine("laissez_faire/scenarios/modern_day_usa.json", llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider)
    engine.run(max_turns=1)
    assert engine.turn == 1


def test_event_system(mock_llm_providers, mock_scorer_llm_provider):
    """
    Tests the event system.
    """
    engine = GameEngine("laissez_faire/scenarios/modern_day_usa.json", llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider)

    # A simple handler that sets a flag
    handler_called = False
    event_payload = None

    def test_handler(data):
        nonlocal handler_called, event_payload
        handler_called = True
        event_payload = data

    engine.register_event_handler("test_event", test_handler)
    engine.trigger_event("test_event", {"key": "value"})

    assert handler_called is True
    assert event_payload == {"key": "value"}

def test_save_and_load_game(mock_llm_providers, mock_scorer_llm_provider):
    """
    Tests that the game can be saved and loaded correctly.
    """
    scenario_path = "laissez_faire/scenarios/modern_day_usa.json"
    save_path = "test_save.json"

    # Create a game, change its state, and save it
    engine1 = GameEngine(scenario_path, llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider)
    engine1.turn = 5
    engine1.save_game(save_path)

    # Create a new game and load the saved state
    engine2 = GameEngine(scenario_path, llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider)
    engine2.load_game(save_path)

    assert engine1.turn == engine2.turn
    assert engine1.scenario == engine2.scenario

    # Clean up the save file
    os.remove(save_path)

def test_scoring_system_and_prompt_generation(mock_scorer_llm_provider):
    """
    Tests the scoring system and the generalized prompt generation.
    """
    scenario_path = "laissez_faire/scenarios/philosophers_debate.json"

    einstein_provider = MagicMock(spec=LLMProvider)
    jobs_provider = MagicMock(spec=LLMProvider)

    mock_llm_providers = {
        "Albert Einstein": einstein_provider,
        "Steve Jobs": jobs_provider
    }

    engine = GameEngine(scenario_path, llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider)

    einstein_provider.get_response.return_value = "Einstein's opening statement."
    jobs_provider.get_response.return_value = "Jobs' counter-argument."
    mock_scorer_llm_provider.get_response.return_value = '{"Einstein": {"eloquence": 1, "logic": 2}, "Jobs": {"eloquence": 2, "logic": 1}}'

    mock_ui = MagicMock()

    engine.run(max_turns=1, ui=mock_ui)

    # Test scoring
    assert engine.scorecard.data["Einstein"]["eloquence"] == 1
    assert engine.scorecard.data["Jobs"]["logic"] == 1
    mock_ui.display_scores.assert_called_once_with(engine.scorecard)

    # Test prompt generation
    einstein_prompt = einstein_provider.get_response.call_args[0][1]
    assert "Turn 1" in einstein_prompt
    assert "Your Current Status:" in einstein_prompt
    assert "Field: Theoretical Physics" in einstein_prompt
    assert "Status of Other Participants:" in einstein_prompt
    assert "Jobs:" in einstein_prompt

    jobs_prompt = jobs_provider.get_response.call_args[0][1]
    assert "Turn 1" in jobs_prompt
    assert "Your Current Status:" in jobs_prompt
    assert "Famous For: Apple Inc., iPhone" in jobs_prompt
    assert "Status of Other Participants:" in jobs_prompt
    assert "Einstein:" in jobs_prompt


def test_run_with_no_ai_players(mock_llm_providers, mock_scorer_llm_provider, capsys):
    """
    Tests that the game can run without any AI players.
    """
    # Create a scenario with no AI players
    scenario = {
        "name": "No AI Scenario",
        "players": [{"name": "Human", "type": "human"}]
    }
    scenario_path = "no_ai_scenario.json"
    with open(scenario_path, "w") as f:
        json.dump(scenario, f)

    engine = GameEngine(scenario_path, llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider)
    engine.run(max_turns=1)

    # Check that the LLM was not called
    for provider in mock_llm_providers.values():
        provider.get_response.assert_not_called()

    # Check the output
    captured = capsys.readouterr()
    assert "No AI players found" in captured.out

    os.remove(scenario_path)

def test_score_turn_invalid_json(mock_llm_providers, mock_scorer_llm_provider, capsys):
    """
    Tests that the engine handles invalid JSON from the LLM during scoring.
    """
    scenario_path = "laissez_faire/scenarios/philosophers_debate.json"
    engine = GameEngine(scenario_path, llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider)

    # Initialize scorecard data
    engine.scorecard.data = {
        "Einstein": {"eloquence": 0, "logic": 0},
        "Jobs": {"eloquence": 0, "logic": 0}
    }

    # Simulate the LLM returning invalid JSON for scores
    mock_scorer_llm_provider.get_response.return_value = "this is not json"

    engine.run(max_turns=1)

    # Check that the error was logged and the scorecard was not updated
    captured = capsys.readouterr()
    assert "Error: Could not decode scores from LLM response." in captured.out
    assert engine.scorecard.data == {"Einstein": {"eloquence": 0, "logic": 0}, "Jobs": {"eloquence": 0, "logic": 0}}
