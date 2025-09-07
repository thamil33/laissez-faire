import json
from .llm import LLMProvider

class GameEngine:
    """
    The main game engine for Laissez Faire.
    """

    def __init__(self, scenario_path, llm_provider: LLMProvider):
        """
        Initializes the game engine with a scenario.

        :param scenario_path: The path to the scenario JSON file.
        """
        self.scenario = self.load_scenario(scenario_path)
        self.turn = 0
        self.event_handlers = {}
        self.llm_provider = llm_provider
        self.history = []
        self.scores = {}

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

    def run(self, max_turns=10, ui=None):
        """
        Runs the main game loop.

        :param max_turns: The maximum number of turns to simulate.
        :param ui: An optional instance of the terminal UI for displaying scores.
        """
        print("Game engine is running...")
        print(f"Loaded scenario: {self.scenario['name']}")

        ai_players = self.get_ai_players()
        if not ai_players:
            print("No AI players found in the scenario. The simulation will run without AI actions.")

        while self.turn < max_turns:
            self.turn += 1
            print(f"--- Turn {self.turn} ---")
            self.trigger_event("turn_start", {"turn": self.turn})

            if ai_players:
                for player in ai_players:
                    # Generate a prompt for the LLM
                    prompt = self.generate_prompt(player)

                    # Get the LLM's action
                    print(f"Getting action for {player['name']}...")
                    action = self.llm_provider.get_response(prompt)
                    print(f"AI Action from {player['name']}: {action}")

                    # Store the action in the history
                    self.history.append({
                        "turn": self.turn,
                        "player": player['name'],
                        "action": action
                    })

            # Score the turn at the end
            self.score_turn(ui=ui)

        print("Game simulation finished.")

    def get_ai_players(self):
        """
        Finds all AI players in the scenario.
        """
        return [p for p in self.scenario.get("players", []) if p.get("type") == "ai"]

    def generate_prompt(self, player):
        """
        Generates a prompt for the LLM based on the current game state.
        This version is more general and data-driven.
        """
        scenario = self.scenario
        player_entity_key = scenario.get("player_entity_key", "countries") # e.g., "countries", "debaters"
        player_entities = scenario.get(player_entity_key, {})

        player_entity_name = player.get("controls") # The name of the entity the player controls
        if not player_entity_name:
            # Fallback for older scenario format
            player_entity_name = player.get("country")

        player_entity_data = player_entities.get(player_entity_name, {})

        prompt = f"You are {player['name']}.\n"
        prompt += f"It is turn {self.turn}.\n"
        prompt += f"Scenario: {scenario['description']}\n\n"

        # Display global parameters
        if "parameters" in scenario and scenario["parameters"]:
            prompt += "Global Context:\n"
            for key, value in scenario["parameters"].items():
                prompt += f"  - {key.replace('_', ' ').title()}: {value}\n"
            prompt += "\n"

        # Display player's entity status
        if player_entity_data:
            prompt += "Your Status:\n"
            for key, value in player_entity_data.items():
                prompt += f"  - {key.replace('_', ' ').title()}: {value}\n"
            prompt += "\n"

        # Display other entities
        if player_entities:
            prompt += "Other Participants:\n"
            for entity_name, entity_data in player_entities.items():
                if entity_name != player_entity_name:
                    prompt += f"  - {entity_name}:\n"
                    # A more advanced implementation could have a "public_attributes" key in the scenario.
                    for key, value in list(entity_data.items())[:3]: # Show first 3 attributes
                        prompt += f"    - {key.replace('_', ' ').title()}: {value}\n"

        prompt += "\nWhat is your next move or statement?"
        return prompt

    def score_turn(self, ui=None):
        """
        Scores the current turn using the LLM.
        """
        print("\n--- Scoring Turn ---")
        scoring_prompt = self.generate_scoring_prompt()
        if not scoring_prompt:
            print("No scoring parameters found in the scenario. Skipping scoring.")
            return

        print("Getting scores from LLM...")
        scores_str = self.llm_provider.get_response(scoring_prompt)
        print(f"LLM Scores: {scores_str}")

        try:
            new_scores = json.loads(scores_str)
            # Update the main scores dictionary
            for player_name, player_scores in new_scores.items():
                if player_name not in self.scores:
                    self.scores[player_name] = {}
                for score_name, score_value in player_scores.items():
                    # For simplicity, we'll just add the new score to the old one
                    self.scores[player_name][score_name] = self.scores[player_name].get(score_name, 0) + score_value
        except (json.JSONDecodeError, TypeError):
            print("Error: Could not decode scores from LLM response.")

        if ui and self.scores:
            ui.display_scores(self.scores)

    def generate_scoring_prompt(self):
        """
        Generates a prompt for the LLM to score the players.
        """
        scenario = self.scenario
        scoring_params = scenario.get("scoring_parameters")
        if not scoring_params:
            return None

        prompt = "You are an impartial judge. Based on the history of actions below, please score each player on the following criteria:\n"
        for param, desc in scoring_params.items():
            prompt += f"  - {param.replace('_', ' ').title()}: {desc}\n"

        prompt += "\nReturn the scores in a JSON format, like this: {\"player_name\": {\"score1\": value, \"score2\": value}}.\n"

        prompt += "\n--- History of Actions ---\n"
        # For now, just use the most recent history to avoid making the prompt too long.
        recent_history = [h for h in self.history if h['turn'] == self.turn]
        for event in recent_history:
            prompt += f"Turn {event['turn']}, {event['player']}: {event['action']}\n"

        return prompt

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
