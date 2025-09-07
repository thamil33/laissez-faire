import json

class GameEngine:
    """
    The main game engine for Laissez Faire.
    """

    def __init__(self, scenario_path):
        """
        Initializes the game engine with a scenario.

        :param scenario_path: The path to the scenario JSON file.
        """
        self.scenario = self.load_scenario(scenario_path)
        self.turn = 0
        self.event_handlers = {}

    def load_scenario(self, scenario_path):
        """
        Loads a scenario from a JSON file.

        :param scenario_path: The path to the scenario JSON file.
        :return: The scenario data as a dictionary.
        """
        with open(scenario_path, 'r') as f:
            return json.load(f)

    def register_event_handler(self, event_type, handler):
        """
        Registers a handler for a specific event type.

        :param event_type: The type of event (e.g., 'economy_update').
        :param handler: The function to call when the event is triggered.
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    def trigger_event(self, event_type, data):
        """
        Triggers an event, calling all registered handlers.

        :param event_type: The type of event to trigger.
        :param data: The data to pass to the event handlers.
        """
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                handler(data)

    def run(self, max_turns=10):
        """
        Runs the main game loop.

        :param max_turns: The maximum number of turns to simulate.
        """
        print("Game engine is running...")
        print(f"Loaded scenario: {self.scenario['name']}")

        while self.turn < max_turns:
            self.turn += 1
            print(f"--- Turn {self.turn} ---")
            self.trigger_event("turn_start", {"turn": self.turn})

        print("Game simulation finished.")

    def save_game(self, save_path):
        """
        Saves the current game state to a file.

        :param save_path: The path to the save file.
        """
        game_state = {
            "turn": self.turn,
            "scenario": self.scenario
            # Note: We are not saving event handlers. This is a simplification.
        }
        with open(save_path, 'w') as f:
            json.dump(game_state, f)

    def load_game(self, save_path):
        """
        Loads a game state from a file.

        :param save_path: The path to the save file.
        """
        with open(save_path, 'r') as f:
            game_state = json.load(f)

        self.turn = game_state["turn"]
        self.scenario = game_state["scenario"]
