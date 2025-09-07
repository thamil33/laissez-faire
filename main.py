import json
from laissez_faire.engine import GameEngine
from laissez_faire.terminal import TerminalUI
from laissez_faire.llm import LLMProvider

def main():
    """
    The main entry point for the Laissez-faire game.
    """
    # Load global LLM provider configurations
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        llm_providers_config = config.get("providers", {})
    except FileNotFoundError:
        print("Warning: config.json not found. Using default 'local' provider.")
        llm_providers_config = {"local": {}}

    scenario_path = "laissez_faire/scenarios/cold_war.json"

    # Load the scenario
    with open(scenario_path, 'r') as f:
        scenario = json.load(f)

    # Helper function to create a provider
    def create_llm_provider(provider_name):
        provider_config = llm_providers_config.get(provider_name, {})
        return LLMProvider(
            model=provider_config.get("model", "local"),
            api_key=provider_config.get("api_key"),
            base_url=provider_config.get("base_url")
        )

    # Create LLM providers for each AI player
    llm_providers = {}
    for player in scenario.get("players", []):
        if player.get("type") == "ai":
            provider_name = player.get("llm_provider", "local")
            llm_providers[player["name"]] = create_llm_provider(provider_name)

    # Create LLM provider for the scorer
    scorer_provider_name = scenario.get("scorer_llm_provider", "local")
    scorer_llm_provider = create_llm_provider(scorer_provider_name)

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
