import json
import os
from laissez_faire.engine import GameEngine
from laissez_faire.terminal import TerminalUI
from laissez_faire.llm import LLMProvider
from rich.console import Console
from rich.prompt import Prompt

def get_safe_path(base_dir, filename):
    """
    Joins a base directory and a filename, and ensures the resulting path is
    within the base directory.
    """
    # Sanitize the filename to prevent directory traversal
    if ".." in filename or filename.startswith("/"):
        print(f"Error: Invalid filename '{filename}'.")
        return None

    # Get the absolute path of the base directory and the intended file
    base_dir_abs = os.path.abspath(base_dir)
    file_path_abs = os.path.abspath(os.path.join(base_dir_abs, filename))

    # Check if the file path is within the base directory
    if os.path.commonpath([base_dir_abs, file_path_abs]) != base_dir_abs:
        print(f"Error: Path traversal attempt detected for filename '{filename}'.")
        return None

    return file_path_abs

def get_providers(config_path="config.json"):
    """
    Loads LLM provider configurations and engine settings from a file.
    """
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        
        providers = config.get("providers", {})
        engine_settings = config.get("engine_settings", {})
        
        return providers, engine_settings
    except FileNotFoundError:
        print(f"Warning: {config_path} not found. LLM providers will not be available.")
        return {}, {}

def create_llm_provider(provider_name, llm_providers_config, summarizer_provider=None):
    """
    Helper function to create a single LLM provider.
    """
    provider_config = llm_providers_config.get(provider_name)
    if not provider_config:
        raise ValueError(f"Provider '{provider_name}' not found in config.json")

    return LLMProvider(
        api_key=provider_config.get("api_key"),
        base_url=provider_config.get("base_url"),
        model_name=provider_config.get("model_name"),
        summarizer_provider=summarizer_provider
    )

def start_new_game(scenario_path, config_path="config.json"):
    """
    Starts a new game from a scenario file.
    """
    llm_providers_config, engine_settings = get_providers(config_path)

    try:
        with open(scenario_path, 'r') as f:
            scenario = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading scenario file: {e}")
        return

    try:
        scorer_provider_name = scenario.get("scorer_llm_provider")
        if not scorer_provider_name:
            raise ValueError("scorer_llm_provider not defined in scenario")
        scorer_llm_provider = create_llm_provider(scorer_provider_name, llm_providers_config)

        llm_providers = {}
        for player in scenario.get("players", []):
            if player.get("type") == "ai":
                provider_name = player.get("llm_provider")
                if not provider_name:
                    raise ValueError(f"llm_provider not defined for player {player['name']}")
                llm_providers[player["name"]] = create_llm_provider(provider_name, llm_providers_config, summarizer_provider=scorer_llm_provider)

    except ValueError as e:
        print(f"Error setting up LLM providers: {e}")
        return

    engine = GameEngine(
        llm_providers=llm_providers,
        scorer_llm_provider=scorer_llm_provider,
        scenario_path=scenario_path,
        engine_settings=engine_settings
    )
    ui = TerminalUI()

    ui.display_welcome(engine.scenario["name"])
    ui.display_scenario_details(engine.scenario)

    engine.run(ui=ui)

def load_saved_game(save_path, config_path="config.json"):
    """
    Loads a game from a save file.
    """
    llm_providers_config, engine_settings = get_providers(config_path)

    try:
        with open(save_path, 'r') as f:
            game_state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading save file: {e}")
        return
    scenario = game_state["scenario"]

    try:
        scorer_provider_name = scenario.get("scorer_llm_provider")
        if not scorer_provider_name:
            raise ValueError("scorer_llm_provider not defined in scenario")
        scorer_llm_provider = create_llm_provider(scorer_provider_name, llm_providers_config)

        llm_providers = {}
        for player in scenario.get("players", []):
            if player.get("type") == "ai":
                provider_name = player.get("llm_provider")
                if not provider_name:
                    raise ValueError(f"llm_provider not defined for player {player['name']}")
                llm_providers[player["name"]] = create_llm_provider(provider_name, llm_providers_config, summarizer_provider=scorer_llm_provider)

    except ValueError as e:
        print(f"Error setting up LLM providers: {e}")
        return

    engine = GameEngine(
        llm_providers=llm_providers,
        scorer_llm_provider=scorer_llm_provider,
        engine_settings=engine_settings
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
    try:
        with open(save_path, 'r') as f:
            game_state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading save file for replay: {e}")
        return

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
        safe_path = get_safe_path(scenarios_dir, scenario_choice)
        if safe_path:
            start_new_game(safe_path)

    elif choice == "Load a saved game":
        saves_dir = "saves"
        if not os.path.exists(saves_dir) or not os.listdir(saves_dir):
            console.print("[bold red]No saved games found.[/bold red]")
            return
        saves = [f for f in os.listdir(saves_dir) if f.endswith(".json")]
        save_choice = Prompt.ask("Choose a save file", choices=saves)
        safe_path = get_safe_path(saves_dir, save_choice)
        if safe_path:
            load_saved_game(safe_path)

    elif choice == "Replay a saved game":
        saves_dir = "saves"
        if not os.path.exists(saves_dir) or not os.listdir(saves_dir):
            console.print("[bold red]No saved games found.[/bold red]")
            return
        saves = [f for f in os.listdir(saves_dir) if f.endswith(".json")]
        save_choice = Prompt.ask("Choose a save file to replay", choices=saves)
        safe_path = get_safe_path(saves_dir, save_choice)
        if safe_path:
            replay_game(safe_path)

if __name__ == "__main__":
    main()
