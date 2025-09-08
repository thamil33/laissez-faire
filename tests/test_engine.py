import pytest
from laissez_faire.engine import GameEngine
from laissez_faire.llm import LLMProvider
import os
import json
from unittest.mock import MagicMock

def test_load_scenario_success(mock_llm_providers, mock_scorer_llm_provider, tmp_path):
    """
    Tests that a scenario is loaded correctly.
    """
    # Create a dummy scenario file
    scenario_content = {"name": "Test Scenario", "start_date": "2024-01-01"}
    scenario_path = tmp_path / "test_scenario.json"
    scenario_path.write_text(json.dumps(scenario_content))

    engine = GameEngine(llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider, scenario_path=str(scenario_path))
    assert engine.scenario["name"] == "Test Scenario"
    assert engine.scenario["start_date"] == "2024-01-01"

def test_load_scenario_file_not_found(mock_llm_providers, mock_scorer_llm_provider):
    """
    Tests that a FileNotFoundError is raised when the scenario file does not exist.
    """
    with pytest.raises(FileNotFoundError):
        GameEngine(llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider, scenario_path="non_existent_scenario.json")

def test_load_scenario_invalid_json(mock_llm_providers, mock_scorer_llm_provider, tmp_path):
    """
    Tests that an error is raised when the scenario file is not valid JSON.
    """
    # Create a dummy invalid scenario file
    scenario_content = '{"name": "Test Scenario", "start_date": "2024-01-01"'
    scenario_path = tmp_path / "invalid_scenario.json"
    scenario_path.write_text(scenario_content)

    with pytest.raises(json.JSONDecodeError):
        GameEngine(llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider, scenario_path=str(scenario_path))


def test_game_engine_run_and_turn_increment(mock_llm_providers, mock_scorer_llm_provider):
    """
    Tests that the game engine's run method executes and increments the turn.
    """
    engine = GameEngine(llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider, scenario_path="laissez_faire/scenarios/modern_day_usa.json")
    engine.run(max_turns=1)
    assert engine.turn == 1


def test_scoring_system_with_function_calling(mock_scorer_llm_provider):
    """
    Tests the scoring system using the new function calling mechanism.
    """
    scenario_path = "laissez_faire/scenarios/philosophers_debate.json"

    einstein_provider = MagicMock(spec=LLMProvider)
    jobs_provider = MagicMock(spec=LLMProvider)

    mock_llm_providers = {
        "Albert Einstein": einstein_provider,
        "Steve Jobs": jobs_provider
    }

    engine = GameEngine(llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider, scenario_path=scenario_path)

    einstein_provider.get_response.return_value = "Einstein's opening statement."
    jobs_provider.get_response.return_value = "Jobs' counter-argument."

    # Simulate the LLM returning a tool call with JSON arguments
    mock_scorer_llm_provider.get_response.return_value = '{"scores": {"Einstein": {"eloquence": 1, "logic": 2, "relevance": 0, "originality": 0}, "Jobs": {"eloquence": 2, "logic": 1, "relevance": 0, "originality": 0}}}'

    mock_ui = MagicMock()

    engine.run(max_turns=1, ui=mock_ui)

    # Test that the scorer's get_response was called with a tool schema
    scorer_call_args = mock_scorer_llm_provider.get_response.call_args
    assert "tools" in scorer_call_args.kwargs
    tools_arg = scorer_call_args.kwargs["tools"]
    assert tools_arg[0]["function"]["name"] == "record_scores"
    assert "eloquence" in tools_arg[0]["function"]["parameters"]["properties"]["scores"]["properties"]["Einstein"]["properties"]

    # Test scoring
    assert engine.scorecard.data["Einstein"]["eloquence"] == 11
    assert engine.scorecard.data["Einstein"]["logic"] == 12
    assert engine.scorecard.data["Jobs"]["eloquence"] == 12
    assert engine.scorecard.data["Jobs"]["logic"] == 11
    mock_ui.display_scores.assert_called_once_with(engine.scorecard)


def test_run_with_no_ai_players(mock_llm_providers, mock_scorer_llm_provider, capsys, tmp_path):
    """
    Tests that the game can run without any AI players.
    """
    # Create a scenario with no AI players
    scenario = {
        "name": "No AI Scenario",
        "players": [{"name": "Human", "type": "human"}]
    }
    scenario_path = tmp_path / "no_ai_scenario.json"
    scenario_path.write_text(json.dumps(scenario))
    engine = GameEngine(llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider, scenario_path=str(scenario_path))
    engine.run(max_turns=1)

    # Check that the LLM was not called
    for provider in mock_llm_providers.values():
        provider.get_response.assert_not_called()

    # Check the output
    captured = capsys.readouterr()
    assert "No AI players found" in captured.out

def test_score_turn_invalid_json(mock_llm_providers, mock_scorer_llm_provider, capsys):
    """
    Tests that the engine handles invalid JSON from the LLM during scoring.
    """
    scenario_path = "laissez_faire/scenarios/philosophers_debate.json"
    engine = GameEngine(llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider, scenario_path=scenario_path)

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

def test_initialize_system_prompts(mock_scorer_llm_provider):
    """
    Tests that system prompts are initialized correctly for AI players.
    """
    scenario_path = "laissez_faire/scenarios/philosophers_debate.json"
    einstein_provider = MagicMock(spec=LLMProvider)
    jobs_provider = MagicMock(spec=LLMProvider)
    mock_llm_providers = {"Albert Einstein": einstein_provider, "Steve Jobs": jobs_provider}

    GameEngine(llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider, scenario_path=scenario_path)

    einstein_provider.get_or_create_history.assert_called_with("Albert Einstein", "You are playing the role of Albert Einstein. Your core argument is that intuition and imagination are the wellspring of true innovation. You should argue that rigorous analysis is a tool, but a subordinate one, used to formalize and verify the insights that come from a deeper, more intuitive place. You can draw on your own experiences with thought experiments (e.g., imagining riding on a beam of light) to illustrate your points. Your tone should be humble, thoughtful, and deeply curious. You are not dismissive of logic, but you see it as a craftsman's tool, not the architect's vision. Your goal is to persuade the audience that without a 'holy curiosity,' and the courage to make intuitive leaps, science and innovation would stagnate.")
    jobs_provider.get_or_create_history.assert_called_with("Steve Jobs", "You are playing the role of Steve Jobs. Your core argument is that innovation is about connecting ideas and that the best connections are often intuitive. You should emphasize that this intuition isn't random; it's a form of pattern recognition that comes from a broad base of knowledge and experience, especially in the liberal arts and design. You believe in a relentless focus on the user experience and that much of the 'analysis' should be in the service of making technology more intuitive and accessible. You can be passionate, sometimes sharp, and always focused on the product and the user. Your goal is to convince the audience that the most profound innovations are not just technically brilliant but also deeply human, and that this requires a kind of 'taste' that can't be purely analytical.")

def test_generate_prompt_with_different_contexts(mock_llm_providers, mock_scorer_llm_provider, tmp_path):
    """
    Tests the prompt generation with various contexts.
    """
    scenario = {
        "name": "Test Scenario",
        "players": [{"name": "Player1", "type": "ai", "controls": "USA"}],
        "player_entity_key": "countries",
        "countries": {
            "USA": {"capital": "Washington D.C.", "population": 330, "economy": "strong"},
            "China": {"capital": "Beijing", "population": 1400}
        },
        "parameters": {"global_tension": "high", "year": 2024}
    }
    scenario_path = tmp_path / "test_generate_prompt.json"
    scenario_path.write_text(json.dumps(scenario))

    engine = GameEngine(llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider, scenario_path=str(scenario_path))
    engine.turn = 1
    prompt = engine.generate_prompt(engine.get_ai_players()[0])

    assert "Turn 1" in prompt
    assert "Global Context:" in prompt
    assert "Global Tension: high" in prompt
    assert "Your Current Status:" in prompt
    assert "Capital: Washington D.C." in prompt
    assert "Status of Other Participants:" in prompt
    assert "China:" in prompt
    assert "Population: 1400" in prompt

def test_run_loop_missing_provider(mock_scorer_llm_provider, capsys):
    """
    Tests that the run loop handles a missing LLM provider for a player.
    """
    scenario_path = "laissez_faire/scenarios/philosophers_debate.json"
    einstein_provider = MagicMock(spec=LLMProvider)
    # No provider for Steve Jobs
    mock_llm_providers = {"Albert Einstein": einstein_provider}

    einstein_provider.get_response.return_value = "Einstein's action"
    engine = GameEngine(llm_providers=mock_llm_providers, scorer_llm_provider=mock_scorer_llm_provider, scenario_path=scenario_path)
    engine.run(max_turns=1)

    captured = capsys.readouterr()
    assert "Warning: No LLM provider found for player Steve Jobs. Skipping turn." in captured.out


def test_generate_scoring_request_no_scoring_parameters(
    mock_llm_providers, mock_scorer_llm_provider, tmp_path
):
    """
    Tests that the scoring request is not generated if there are no scoring
    parameters in the scenario.
    """
    scenario = {"name": "Test Scenario", "players": []}
    scenario_path = tmp_path / "test_scenario.json"
    scenario_path.write_text(json.dumps(scenario))

    engine = GameEngine(
        llm_providers=mock_llm_providers,
        scorer_llm_provider=mock_scorer_llm_provider,
        scenario_path=str(scenario_path),
    )
    prompt, tools = engine._generate_scoring_request()
    assert prompt is None
    assert tools is None


def test_get_ai_players_missing_type(
    mock_llm_providers, mock_scorer_llm_provider, tmp_path
):
    """
    Tests that a player with a missing 'type' key is not considered an AI player.
    """
    scenario = {
        "name": "Test Scenario",
        "players": [{"name": "Player1"}],
    }
    scenario_path = tmp_path / "test_scenario.json"
    scenario_path.write_text(json.dumps(scenario))

    engine = GameEngine(
        llm_providers=mock_llm_providers,
        scorer_llm_provider=mock_scorer_llm_provider,
        scenario_path=str(scenario_path),
    )
    ai_players = engine.get_ai_players()
    assert len(ai_players) == 0


def test_save_game_no_scorecard(
    mock_llm_providers, mock_scorer_llm_provider, tmp_path
):
    """
    Tests that the game can be saved correctly when there is no scorecard.
    """
    scenario = {"name": "Test Scenario", "players": []}
    scenario_path = tmp_path / "test_scenario.json"
    scenario_path.write_text(json.dumps(scenario))
    save_path = tmp_path / "save.json"

    engine = GameEngine(
        llm_providers=mock_llm_providers,
        scorer_llm_provider=mock_scorer_llm_provider,
        scenario_path=str(scenario_path),
    )
    engine.save_game(str(save_path))

    assert save_path.exists()
    with open(save_path, "r") as f:
        game_state = json.load(f)
    assert game_state["scorecard"] == {}


def test_load_game_no_scorecard(
    mock_llm_providers, mock_scorer_llm_provider, tmp_path
):
    """
    Tests that the game can be loaded correctly when there is no scorecard.
    """
    scenario = {"name": "Test Scenario", "players": []}
    scenario_path = tmp_path / "test_scenario.json"
    scenario_path.write_text(json.dumps(scenario))
    save_path = tmp_path / "save.json"

    game_state = {
        "turn": 1,
        "scenario": scenario,
        "history": [],
        "scorecard": {},
    }
    save_path.write_text(json.dumps(game_state))

    engine = GameEngine(
        llm_providers=mock_llm_providers,
        scorer_llm_provider=mock_scorer_llm_provider,
        scenario_path=str(scenario_path),
    )
    engine.load_game(str(save_path))

    assert engine.scorecard is None
