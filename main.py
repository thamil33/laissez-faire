import json
import os
from laissez_faire.engine import GameEngine
from laissez_faire.terminal import TerminalUI
from laissez_faire.llm import LLMProvider
from rich.console import Console
from rich.prompt import Prompt

def get_providers(config_path="config.json"):
    """
    Loads LLM provider configurations from a file.
    """
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config.get("providers", {})
    except FileNotFoundError:
        print(f"Warning: {config_path} not found. Using default 'local' provider.")
        return {"local": {}}

def create_llm_provider(provider_name, llm_providers_config):
    """
    Helper function to create a single LLM provider.
    """
    provider_config = llm_providers_config.get(provider_name, {})
    return LLMProvider(
        model=provider_config.get("model", "local"),
        api_key=provider_config.get("api_key"),
        base_url=provider_config.get("base_url")
    )

def start_new_game(scenario_path, config_path="config.json"):
    """
    Starts a new game from a scenario file.
    """
    llm_providers_config = get_providers(config_path)

    with open(scenario_path, 'r') as f:
        scenario = json.load(f)

    llm_providers = {}
    for player in scenario.get("players", []):
        if player.get("type") == "ai":
            provider_name = player.get("llm_provider", "local")
            llm_providers[player["name"]] = create_llm_provider(provider_name, llm_providers_config)

    scorer_provider_name = scenario.get("scorer_llm_provider", "local")
    scorer_llm_provider = create_llm_provider(scorer_provider_name, llm_providers_config)

    engine = GameEngine(
        llm_providers=llm_providers,
        scorer_llm_provider=scorer_llm_provider,
        scenario_path=scenario_path
    )
    ui = TerminalUI()

    ui.display_welcome(engine.scenario["name"])
    ui.display_scenario_details(engine.scenario)

    engine.run(ui=ui)

def load_saved_game(save_path, config_path="config.json"):
    """
    Loads a game from a save file.
    """
    llm_providers_config = get_providers(config_path)

    with open(save_path, 'r') as f:
        game_state = json.load(f)
    scenario = game_state["scenario"]

    llm_providers = {}
    for player in scenario.get("players", []):
        if player.get("type") == "ai":
            provider_name = player.get("llm_provider", "local")
            llm_providers[player["name"]] = create_llm_provider(provider_name, llm_providers_config)

    scorer_provider_name = scenario.get("scorer_llm_provider", "local")
    scorer_llm_provider = create_llm_provider(scorer_provider_name, llm_providers_config)

    engine = GameEngine(
        llm_providers=llm_providers,
        scorer_llm_provider=scorer_llm_provider
    )
    engine.load_game(save_path)
    ui = TerminalUI()

    ui.display_welcome(engine.scenario["name"])
    print("\n--- Game Loaded ---")
    ui.display_scores(engine.scorecard)

    engine.run(ui=ui)

def replay_game(save_path):
    """
    Replays a game from a save file.
    """
    with open(save_path, 'r') as f:
        game_state = json.load(f)

    scenario = game_state["scenario"]
    history = game_state["history"]

    ui = TerminalUI()
    ui.display_welcome(scenario["name"])
    ui.display_scenario_details(scenario)

    console = Console()
    console.print("\n[bold green]--- Replay Started ---[/bold green]")

    for turn_number in range(1, game_state["turn"] + 1):
        console.print(f"\n[bold]--- Turn {turn_number} ---[/bold]")
        turn_actions = [h for h in history if h["turn"] == turn_number]
        for action in turn_actions:
            console.print(f"[cyan]{action['player']}:[/cyan] {action['action']}")

        if turn_number < game_state["turn"]:
            Prompt.ask("Press Enter to continue to the next turn...")

    console.print("\n[bold green]--- Replay Finished ---[/bold green]")

def main():
    """
    The main entry point for the Laissez-faire game.
    """
    console = Console()
    console.print("[bold blue]Welcome to Laissez Faire![/bold blue]")

    actions = ["Start a new game", "Load a saved game", "Replay a saved game"]
    choice = Prompt.ask("What would you like to do?", choices=actions, default="Start a new game")

    if choice == "Start a new game":
        scenarios_dir = "laissez_faire/scenarios"
        scenarios = [f for f in os.listdir(scenarios_dir) if f.endswith(".json")]
        scenario_choice = Prompt.ask("Choose a scenario", choices=scenarios)
        start_new_game(os.path.join(scenarios_dir, scenario_choice))

    elif choice == "Load a saved game":
        saves_dir = "saves"
        if not os.path.exists(saves_dir) or not os.listdir(saves_dir):
            console.print("[bold red]No saved games found.[/bold red]")
            return
        saves = [f for f in os.listdir(saves_dir) if f.endswith(".json")]
        save_choice = Prompt.ask("Choose a save file", choices=saves)
        load_saved_game(os.path.join(saves_dir, save_choice))

    elif choice == "Replay a saved game":
        saves_dir = "saves"
        if not os.path.exists(saves_dir) or not os.listdir(saves_dir):
            console.print("[bold red]No saved games found.[/bold red]")
            return
        saves = [f for f in os.listdir(saves_dir) if f.endswith(".json")]
        save_choice = Prompt.ask("Choose a save file to replay", choices=saves)
        replay_game(os.path.join(saves_dir, save_choice))

if __name__ == "__main__":
    main()
