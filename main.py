from laissez_faire.engine import GameEngine
from laissez_faire.terminal import TerminalUI

def main():
    """
    The main entry point for the Laissez Faire game.
    """
    scenario_path = "laissez_faire/scenarios/modern_day_usa.json"

    # Initialize the game engine and terminal UI
    engine = GameEngine(scenario_path)
    ui = TerminalUI()

    # Display the welcome message and scenario details
    ui.display_welcome(engine.scenario["name"])
    ui.display_scenario_details(engine.scenario)

    # Run the game
    engine.run()

if __name__ == "__main__":
    main()
