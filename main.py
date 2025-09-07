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

    scenario_path = "laissez_faire/scenarios/cold_war.json"

    # Load the scenario to get LLM configurations
    with open(scenario_path, 'r') as f:
        scenario = json.load(f)

    # Create LLM providers for each AI player
    llm_providers = {}
    for player in scenario.get("players", []):
        if player.get("type") == "ai":
            llm_config = player.get("llm_config", {})
            provider = LLMProvider(
                model=llm_config.get("model", "local"),
                api_key=llm_config.get("api_key"),
                base_url=llm_config.get("base_url")
            )
            llm_providers[player["name"]] = provider

    # Create LLM provider for the scorer
    scorer_llm_config = scenario.get("scorer_llm_config", {})
    scorer_llm_provider = LLMProvider(
        model=scorer_llm_config.get("model", "local"),
        api_key=scorer_llm_config.get("api_key"),
        base_url=scorer_llm_config.get("base_url")
    )

    # Initialize the game engine and terminal UI
    engine = GameEngine(
        scenario_path,
        llm_providers=llm_providers,
        scorer_llm_provider=scorer_llm_provider
    )
    ui = TerminalUI()

    # Display the welcome message and scenario details
    ui.display_welcome(engine.scenario["name"])
    ui.display_scenario_details(engine.scenario)

    # Run the game
    engine.run(ui=ui)

if __name__ == "__main__":
    main()
