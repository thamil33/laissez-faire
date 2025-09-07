import pytest
import os
import json
from unittest.mock import MagicMock
from laissez_faire.engine import GameEngine
from laissez_faire.llm import LLMProvider

@pytest.fixture
def mock_llm_providers():
    """Fixture for a mock LLM providers dictionary."""
    return {"player1": MagicMock(spec=LLMProvider)}

@pytest.fixture
def mock_scorer_llm_provider():
    """Fixture for a mock scorer LLM provider."""
    return MagicMock(spec=LLMProvider)

@pytest.fixture
def scenario_path():
    """Fixture for a dummy scenario file."""
    scenario_content = {
        "name": "Test Scenario",
        "players": [{"name": "player1", "type": "ai"}],
        "scorer_llm_provider": "local"
    }
    scenario_path = "test_scenario.json"
    with open(scenario_path, "w") as f:
        json.dump(scenario_content, f)
    yield scenario_path
    os.remove(scenario_path)

def test_save_game(mock_llm_providers, mock_scorer_llm_provider, scenario_path, tmp_path):
    """
    Tests that the game can be saved correctly.
    """
    save_path = tmp_path / "save.json"
    engine = GameEngine(
        llm_providers=mock_llm_providers,
        scorer_llm_provider=mock_scorer_llm_provider,
        scenario_path=scenario_path
    )
    engine.turn = 5
    engine.history.append({"turn": 1, "player": "player1", "action": "test action"})

    engine.save_game(save_path)

    assert os.path.exists(save_path)
    with open(save_path, 'r') as f:
        game_state = json.load(f)

    assert game_state["turn"] == 5
    assert game_state["history"][0]["action"] == "test action"

def test_load_game(mock_llm_providers, mock_scorer_llm_provider, scenario_path, tmp_path):
    """
    Tests that the game can be loaded correctly.
    """
    save_path = tmp_path / "save.json"

    # Create a save file
    game_state = {
        "turn": 3,
        "scenario": {"name": "Loaded Scenario", "players": []},
        "history": [{"turn": 1, "player": "player1", "action": "loaded action"}],
        "scorecard": {}
    }
    with open(save_path, 'w') as f:
        json.dump(game_state, f)

    engine = GameEngine(
        llm_providers=mock_llm_providers,
        scorer_llm_provider=mock_scorer_llm_provider
    )
    engine.load_game(save_path)

    assert engine.turn == 3
    assert engine.scenario["name"] == "Loaded Scenario"
    assert engine.history[0]["action"] == "loaded action"

def test_auto_save(mock_llm_providers, mock_scorer_llm_provider, scenario_path):
    """
    Tests that the game is auto-saved after each turn.
    """
    if os.path.exists("saves/autosave.json"):
        os.remove("saves/autosave.json")

    engine = GameEngine(
        llm_providers=mock_llm_providers,
        scorer_llm_provider=mock_scorer_llm_provider,
        scenario_path=scenario_path
    )

    # Mock the LLM provider to return a response
    mock_llm_providers["player1"].get_response.return_value = "auto-save action"

    engine.run(max_turns=1)

    assert os.path.exists("saves/autosave.json")
    with open("saves/autosave.json", 'r') as f:
        game_state = json.load(f)

    assert game_state["turn"] == 1
    assert game_state["history"][0]["action"] == "auto-save action"

    if os.path.exists("saves/autosave.json"):
        os.remove("saves/autosave.json")
