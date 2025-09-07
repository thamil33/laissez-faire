import pytest
from laissez_faire.engine import GameEngine
import os
import json

def test_load_scenario_success():
    """
    Tests that a scenario is loaded correctly.
    """
    # Create a dummy scenario file
    scenario_content = '{"name": "Test Scenario", "start_date": "2024-01-01"}'
    scenario_path = "test_scenario.json"
    with open(scenario_path, "w") as f:
        f.write(scenario_content)

    engine = GameEngine(scenario_path)
    assert engine.scenario["name"] == "Test Scenario"
    assert engine.scenario["start_date"] == "2024-01-01"

    # Clean up the dummy file
    os.remove(scenario_path)

def test_load_scenario_file_not_found():
    """
    Tests that a FileNotFoundError is raised when the scenario file does not exist.
    """
    with pytest.raises(FileNotFoundError):
        GameEngine("non_existent_scenario.json")

def test_load_scenario_invalid_json():
    """
    Tests that an error is raised when the scenario file is not valid JSON.
    """
    # Create a dummy invalid scenario file
    scenario_content = '{"name": "Test Scenario", "start_date": "2024-01-01"'
    scenario_path = "invalid_scenario.json"
    with open(scenario_path, "w") as f:
        f.write(scenario_content)

    with pytest.raises(json.JSONDecodeError):
        GameEngine(scenario_path)

    # Clean up the dummy file
    os.remove(scenario_path)


def test_game_engine_run_and_turn_increment():
    """
    Tests that the game engine's run method executes and increments the turn.
    """
    engine = GameEngine("laissez_faire/scenarios/modern_day_usa.json")
    engine.run(max_turns=1)
    assert engine.turn == 1


def test_event_system():
    """
    Tests the event system.
    """
    engine = GameEngine("laissez_faire/scenarios/modern_day_usa.json")

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

def test_save_and_load_game():
    """
    Tests that the game can be saved and loaded correctly.
    """
    scenario_path = "laissez_faire/scenarios/modern_day_usa.json"
    save_path = "test_save.json"

    # Create a game, change its state, and save it
    engine1 = GameEngine(scenario_path)
    engine1.turn = 5
    engine1.save_game(save_path)

    # Create a new game and load the saved state
    engine2 = GameEngine(scenario_path)
    engine2.load_game(save_path)

    assert engine1.turn == engine2.turn
    assert engine1.scenario == engine2.scenario

    # Clean up the save file
    os.remove(save_path)
