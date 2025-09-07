import pytest
from laissez_faire.engine import GameEngine
from laissez_faire.llm import LLMProvider
import os
import json
from unittest.mock import Mock

@pytest.fixture
def mock_llm_provider():
    """Fixture for a mock LLM provider."""
    return Mock(spec=LLMProvider)

def test_load_scenario_success(mock_llm_provider):
    """
    Tests that a scenario is loaded correctly.
    """
    # Create a dummy scenario file
    scenario_content = '{"name": "Test Scenario", "start_date": "2024-01-01"}'
    scenario_path = "test_scenario.json"
    with open(scenario_path, "w") as f:
        f.write(scenario_content)

    engine = GameEngine(scenario_path, llm_provider=mock_llm_provider)
    assert engine.scenario["name"] == "Test Scenario"
    assert engine.scenario["start_date"] == "2024-01-01"

    # Clean up the dummy file
    os.remove(scenario_path)

def test_load_scenario_file_not_found(mock_llm_provider):
    """
    Tests that a FileNotFoundError is raised when the scenario file does not exist.
    """
    with pytest.raises(FileNotFoundError):
        GameEngine("non_existent_scenario.json", llm_provider=mock_llm_provider)

def test_load_scenario_invalid_json(mock_llm_provider):
    """
    Tests that an error is raised when the scenario file is not valid JSON.
    """
    # Create a dummy invalid scenario file
    scenario_content = '{"name": "Test Scenario", "start_date": "2024-01-01"'
    scenario_path = "invalid_scenario.json"
    with open(scenario_path, "w") as f:
        f.write(scenario_content)

    with pytest.raises(json.JSONDecodeError):
        GameEngine(scenario_path, llm_provider=mock_llm_provider)

    # Clean up the dummy file
    os.remove(scenario_path)


def test_game_engine_run_and_turn_increment(mock_llm_provider):
    """
    Tests that the game engine's run method executes and increments the turn.
    """
    engine = GameEngine("laissez_faire/scenarios/modern_day_usa.json", llm_provider=mock_llm_provider)
    engine.run(max_turns=1)
    assert engine.turn == 1


def test_event_system(mock_llm_provider):
    """
    Tests the event system.
    """
    engine = GameEngine("laissez_faire/scenarios/modern_day_usa.json", llm_provider=mock_llm_provider)

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

def test_save_and_load_game(mock_llm_provider):
    """
    Tests that the game can be saved and loaded correctly.
    """
    scenario_path = "laissez_faire/scenarios/modern_day_usa.json"
    save_path = "test_save.json"

    # Create a game, change its state, and save it
    engine1 = GameEngine(scenario_path, llm_provider=mock_llm_provider)
    engine1.turn = 5
    engine1.save_game(save_path)

    # Create a new game and load the saved state
    engine2 = GameEngine(scenario_path, llm_provider=mock_llm_provider)
    engine2.load_game(save_path)

    assert engine1.turn == engine2.turn
    assert engine1.scenario == engine2.scenario

    # Clean up the save file
    os.remove(save_path)

def test_scoring_system_and_prompt_generation(mock_llm_provider):
    """
    Tests the scoring system and the generalized prompt generation.
    """
    scenario_path = "laissez_faire/scenarios/philosophers_debate.json"
    engine = GameEngine(scenario_path, llm_provider=mock_llm_provider)

    mock_llm_provider.get_response.side_effect = [
        "Einstein's opening statement.",
        "Jobs' counter-argument.",
        '{"Albert Einstein": {"eloquence": 1, "logic": 2}, "Steve Jobs": {"eloquence": 2, "logic": 1}}'
    ]

    mock_ui = Mock()

    engine.run(max_turns=1, ui=mock_ui)

    # Test scoring
    assert engine.scores["Albert Einstein"]["eloquence"] == 1
    assert engine.scores["Steve Jobs"]["logic"] == 1
    mock_ui.display_scores.assert_called_once_with(engine.scores)

    # Test prompt generation
    # The mock was called 3 times. The first call was for Einstein's action.
    einstein_prompt = mock_llm_provider.get_response.call_args_list[0][0][0]
    assert "You are Albert Einstein" in einstein_prompt
    assert "Topic: The role of intuition versus rigorous analysis" in einstein_prompt
    assert "Your Status:" in einstein_prompt
    assert "Field: Theoretical Physics" in einstein_prompt
    assert "Other Participants:" in einstein_prompt
    assert "Jobs:" in einstein_prompt

    # The second call was for Jobs' action.
    jobs_prompt = mock_llm_provider.get_response.call_args_list[1][0][0]
    assert "You are Steve Jobs" in jobs_prompt
    assert "Famous For: Apple Inc., iPhone" in jobs_prompt
    assert "Einstein:" in jobs_prompt
