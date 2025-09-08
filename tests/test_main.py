import pytest
from unittest.mock import patch
import json
import os
from main import start_new_game

@pytest.fixture
def mock_game_engine():
    """Fixture for a mock GameEngine."""
    with patch('main.GameEngine') as mock:
        yield mock

@pytest.fixture
def mock_terminal_ui():
    """Fixture for a mock TerminalUI."""
    with patch('main.TerminalUI') as mock:
        yield mock

@pytest.fixture
def mock_llm_provider():
    """Fixture for a mock LLMProvider."""
    with patch('main.LLMProvider') as mock:
        yield mock

def test_run_game_success(mock_game_engine, mock_terminal_ui, mock_llm_provider, tmp_path):
    """
    Tests that the start_new_game function can be called successfully.
    """
    # Create dummy scenario and config files
    scenario = {
        "name": "Test Scenario",
        "players": [{"name": "Player1", "type": "ai", "llm_provider": "test_provider"}],
        "scorer_llm_provider": "test_provider"
    }
    config = {
        "providers": {
            "test_provider": {
                "model_name": "test_model",
                "api_key": "test_key"
            }
        }
    }

    scenario_path = tmp_path / "test_scenario.json"
    scenario_path.write_text(json.dumps(scenario))
    config_path = tmp_path / "test_config.json"
    config_path.write_text(json.dumps(config))

    start_new_game(str(scenario_path), str(config_path))

    mock_game_engine.assert_called_once()
    mock_terminal_ui.assert_called_once()

    # Check that the engine's run method was called
    mock_game_engine.return_value.run.assert_called_once()

    # Check that the UI methods were called
    mock_terminal_ui.return_value.display_welcome.assert_called_once()
    mock_terminal_ui.return_value.display_scenario_details.assert_called_once()


def test_run_game_config_not_found(mock_game_engine, mock_terminal_ui, mock_llm_provider, capsys, tmp_path):
    """
    Tests that the game exits gracefully if the config file is not found.
    """
    scenario = {"name": "Test Scenario", "players": [], "scorer_llm_provider": "test_provider"}
    scenario_path = tmp_path / "test_scenario.json"
    scenario_path.write_text(json.dumps(scenario))

    start_new_game(str(scenario_path), "non_existent_config.json")

    mock_game_engine.assert_not_called()

    # Check the warning message
    captured = capsys.readouterr()
    assert "non_existent_config.json not found" in captured.out
    assert "Error setting up LLM providers" in captured.out
