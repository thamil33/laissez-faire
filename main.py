import json
from laissez_faire.engine import GameEngine
from laissez_faire.terminal import TerminalUI
from laissez_faire.llm import LLMProvider

def main():
    """
    The main entry point for the Laissez Faire game.
    """
    # Load configuration
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}

    llm_config = config.get("llm_provider", {})

    scenario_path = "laissez_faire/scenarios/philosophers_debate.json"

    # Initialize the LLM provider
    llm_provider = LLMProvider(
        model=llm_config.get("model", "local"),
        api_key=llm_config.get("api_key"),
        base_url=llm_config.get("base_url")
    )

    # Initialize the game engine and terminal UI
    engine = GameEngine(scenario_path, llm_provider=llm_provider)
    ui = TerminalUI()

    # Display the welcome message and scenario details
    ui.display_welcome(engine.scenario["name"])
    ui.display_scenario_details(engine.scenario)

    # Run the game
    engine.run(ui=ui)

if __name__ == "__main__":
    main()
