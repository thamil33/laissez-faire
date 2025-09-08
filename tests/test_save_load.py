import pytest
import os
import json
from unittest.mock import MagicMock
from laissez_faire.engine import GameEngine
from laissez_faire.llm import LLMProvider


@pytest.fixture
def scenario_path(tmp_path):
    """Fixture for a dummy scenario file path."""
    scenario_content = {
        "name": "Test Scenario",
        "players": [{"name": "player1", "type": "ai"}],
        "scorer_llm_provider": "local",
    }
    scenario_file = tmp_path / "test_scenario.json"
    scenario_file.write_text(json.dumps(scenario_content))
    return str(scenario_file)


def test_save_game(
    mock_llm_providers, mock_scorer_llm_provider, scenario_path, tmp_path
):
    """
    Tests that the game can be saved correctly.
    """
    save_path = tmp_path / "save.json"
    engine = GameEngine(
        llm_providers=mock_llm_providers,
        scorer_llm_provider=mock_scorer_llm_provider,
        scenario_path=scenario_path,
    )
    engine.turn = 5
    engine.history.append({"turn": 1, "player": "player1", "action": "test action"})

    engine.save_game(str(save_path))

    assert save_path.exists()
    with open(save_path, "r") as f:
        game_state = json.load(f)

    assert game_state["turn"] == 5
    assert game_state["history"][0]["action"] == "test action"


def test_load_game(
    mock_llm_providers, mock_scorer_llm_provider, scenario_path, tmp_path
):
    """
    Tests that the game can be loaded correctly.
    """
    save_path = tmp_path / "save.json"

    # Create a save file
    game_state = {
        "turn": 3,
        "scenario": {"name": "Loaded Scenario", "players": []},
        "history": [{"turn": 1, "player": "player1", "action": "loaded action"}],
        "scorecard": {},
    }
    save_path.write_text(json.dumps(game_state))

    engine = GameEngine(
        llm_providers=mock_llm_providers,
        scorer_llm_provider=mock_scorer_llm_provider,
        scenario_path=scenario_path,
    )
    engine.load_game(str(save_path))

    assert engine.turn == 3
    assert engine.scenario["name"] == "Loaded Scenario"
    assert engine.history[0]["action"] == "loaded action"


def test_auto_save(
    mock_llm_providers, mock_scorer_llm_provider, scenario_path, tmp_path
):
    """
    Tests that the game is auto-saved after each turn.
    """
    # Set the saves directory to a temporary directory
    saves_dir = tmp_path / "saves"
    saves_dir.mkdir()

    engine = GameEngine(
        llm_providers=mock_llm_providers,
        scorer_llm_provider=mock_scorer_llm_provider,
        scenario_path=scenario_path,
        saves_dir=str(saves_dir),
    )

    # Mock the LLM provider to return a response
    mock_llm_providers["player1"].get_response.return_value = "auto-save action"

    engine.run(max_turns=1)

    autosave_path = saves_dir / "autosave.json"
    assert autosave_path.exists()
    with open(autosave_path, "r") as f:
        game_state = json.load(f)

    assert game_state["turn"] == 1
    assert game_state["history"][0]["action"] == "auto-save action"
