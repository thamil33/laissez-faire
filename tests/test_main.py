import pytest
from unittest.mock import patch, MagicMock
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

def test_run_game_success(mock_game_engine, mock_terminal_ui, mock_llm_provider):
    """
    Tests that the start_new_game function can be called successfully.
    """
    # Create dummy scenario and config files
    scenario = {"name": "Test Scenario", "players": []}
    config = {"providers": {"local": {}}}

    with open("test_scenario.json", "w") as f:
        json.dump(scenario, f)
    with open("test_config.json", "w") as f:
        json.dump(config, f)

    start_new_game("test_scenario.json", "test_config.json")

    mock_game_engine.assert_called_once()
    mock_terminal_ui.assert_called_once()

    # Check that the engine's run method was called
    mock_game_engine.return_value.run.assert_called_once()

    # Check that the UI methods were called
    mock_terminal_ui.return_value.display_welcome.assert_called_once()
    mock_terminal_ui.return_value.display_scenario_details.assert_called_once()

    os.remove("test_scenario.json")
    os.remove("test_config.json")

def test_run_game_config_not_found(mock_game_engine, mock_terminal_ui, mock_llm_provider, capsys):
    """
    Tests that the game can run without a config file.
    """
    scenario = {"name": "Test Scenario", "players": []}
    with open("test_scenario.json", "w") as f:
        json.dump(scenario, f)

    start_new_game("test_scenario.json", "non_existent_config.json")

    mock_game_engine.assert_called_once()
    mock_terminal_ui.assert_called_once()

    # Check the warning message
    captured = capsys.readouterr()
    assert "non_existent_config.json not found" in captured.out

    os.remove("test_scenario.json")
