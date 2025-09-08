import json
import re
import os
import operator

from .llm import LLMProvider

class Scorecard:
    """
    Manages the scorecard for the game.
    """
    def __init__(self, scenario):
        self.template = scenario.get("scorecard", {})
        self.scoring_parameters = scenario.get("scoring_parameters", {})
        self.data = {}

    def _safe_eval(self, expr, context):
        """
        A safe evaluator for simple arithmetic expressions.
        """
        # Allowed operators
        ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv
        }

        # Check for unsupported operators first
        unsupported_ops = set(re.findall(r'[^\w\s.()]', expr)) - set(ops.keys())
        if unsupported_ops:
            raise ValueError(f"Unsupported operator: {unsupported_ops.pop()}")

        # remove parentheses
        expr = expr.replace("(", "").replace(")", "")
        # Regular expression to safely parse the expression
        # This will split the expression by operators, keeping the operators
        parts = re.split(r' *([+\-*/]) *', expr)

        # The first part should be a variable or a number
        try:
            # Get the value from the context or parse it as a float
            if parts[0] in context:
                acc = context[parts[0]]
            else:
                acc = float(parts[0])
        except (ValueError, KeyError):
            raise ValueError(f"Invalid expression: unknown variable or number {parts[0]}")

        # Process the rest of the parts (operator and operand)
        for i in range(1, len(parts), 2):
            op_str = parts[i]
            operand_str = parts[i+1]

            if op_str not in ops:
                raise ValueError(f"Unsupported operator: {op_str}")

            try:
                if operand_str in context:
                    operand = context[operand_str]
                else:
                    operand = float(operand_str)
            except (ValueError, KeyError):
                raise ValueError(f"Invalid expression: unknown variable or number {operand_str}")

            # Perform the operation
            acc = ops[op_str](acc, operand)

        return acc

    def update(self, llm_scores):
        """
        Updates the scorecard data based on the LLM's scores.
        """
        for player, scores in llm_scores.items():
            if player not in self.data:
                self.data[player] = {}

            for score_name, value in scores.items():
                config = self.scoring_parameters.get(score_name)
                if not config:
                    continue

                score_type = config.get("type")
                if score_type == "absolute":
                    self.data[player][score_name] = value
                elif score_type == "calculated":
                    calculation = config.get("calculation")
                    current_value = self.data[player].get(score_name, 0)

                    try:
                        new_value = self._safe_eval(calculation, {
                            "current_value": current_value,
                            "llm_judgement": value
                        })
                        self.data[player][score_name] = new_value
                    except ValueError as e:
                        print(f"Error calculating score for {score_name}: {e}")


    def render(self):
        """
        Renders the scorecard based on the template.
        """
        render_type = self.template.get("render_type", "text")
        if render_type == 'json':
            return json.dumps(self.data, indent=2)

        output = self.template.get('template', '')

        placeholders = re.findall(r'\{(\w+)\.(\w+)\}', output)
        for player, score in placeholders:
            value = self.data.get(player, {}).get(score, 0)
            output = output.replace(f'{{{player}.{score}}}', str(value))

        return output

class GameEngine:
    """
    The main game engine for Laissez-faire.
    """

    def __init__(self, llm_providers: dict, scorer_llm_provider: LLMProvider, scenario_path=None, saves_dir="saves"):
        """
        Initializes the game engine.
        :param llm_providers: A dictionary of LLM providers for each player.
        :param scorer_llm_provider: An LLM provider for the scorer.
        :param scenario_path: The path to the scenario JSON file (optional).
        """
        self.scenario = self.load_scenario(scenario_path) if scenario_path else {}
        self.turn = 0
        self.llm_providers = llm_providers
        self.scorer_llm_provider = scorer_llm_provider
        self.history = []
        self.scorecard = None
        self.saves_dir = saves_dir

        if self.scenario:
            self.initialize_system_prompts()

            if "scorecard" in self.scenario:
                self.scorecard = Scorecard(self.scenario)
                # Initialize the scorecard with data from the scenario
                player_entity_key = self.scenario.get("player_entity_key")
                if player_entity_key and player_entity_key in self.scenario:
                    initial_data = self.scenario[player_entity_key]
                    for player, data in initial_data.items():
                        if player not in self.scorecard.data:
                            self.scorecard.data[player] = {}
                        for key, value in data.items():
                            self.scorecard.data[player][key] = value

    def initialize_system_prompts(self):
        """
        Initializes the conversation history for each AI player with their system prompt.
        """
        for player in self.get_ai_players():
            provider = self.llm_providers.get(player['name'])
            if provider:
                system_prompt = player.get("system_prompt")
                if system_prompt:
                    provider.get_or_create_history(player['name'], system_prompt)

    def load_scenario(self, scenario_path):
        """
        Loads a scenario from a JSON file.

        :param scenario_path: The path to the scenario JSON file.
        :return: The scenario data as a dictionary.
        """
        with open(scenario_path, 'r') as f:
            return json.load(f)

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

            if ai_players:
                for player in ai_players:
                    # Generate a prompt for the LLM
                    prompt = self.generate_prompt(player)

                    # Get the LLM's action
                    print(f"Getting action for {player['name']}...")
                    provider = self.llm_providers.get(player['name'])
                    if not provider:
                        print(f"Warning: No LLM provider found for player {player['name']}. Skipping turn.")
                        continue
                    action = provider.get_response(player['name'], prompt)
                    print(f"AI Action from {player['name']}: {action}")

                    # Store the action in the history
                    self.history.append({
                        "turn": self.turn,
                        "player": player['name'],
                        "action": action
                    })

            # Score the turn at the end
            self.score_turn()
            if ui and self.scorecard:
                ui.display_scores(self.scorecard)

            # Auto-save the game
            if not os.path.exists(self.saves_dir):
                os.makedirs(self.saves_dir)
            self.save_game(os.path.join(self.saves_dir, "autosave.json"))
            print("Game auto-saved.")

        print("Game simulation finished.")

    def get_ai_players(self):
        """
        Finds all AI players in the scenario.
        """
        return [p for p in self.scenario.get("players", []) if p.get("type") == "ai"]

    def generate_prompt(self, player):
        """
        Generates a prompt for the LLM based on the current game state.
        This prompt provides the turn-specific context.
        """
        scenario = self.scenario
        player_entity_key = scenario.get("player_entity_key", "countries")
        player_entities = scenario.get(player_entity_key, {})

        player_entity_name = player.get("controls")
        player_entity_data = player_entities.get(player_entity_name, {})

        prompt = f"It is now Turn {self.turn}.\n"

        # Add dynamic context to the prompt
        if "parameters" in scenario and scenario["parameters"]:
            prompt += "\nGlobal Context:\n"
            for key, value in scenario["parameters"].items():
                prompt += f"  - {key.replace('_', ' ').title()}: {value}\n"

        if player_entity_data:
            prompt += "\nYour Current Status:\n"
            for key, value in player_entity_data.items():
                prompt += f"  - {key.replace('_', ' ').title()}: {value}\n"

        if player_entities:
            prompt += "\nStatus of Other Participants:\n"
            for entity_name, entity_data in player_entities.items():
                if entity_name != player_entity_name:
                    prompt += f"  - {entity_name}:\n"
                    for key, value in list(entity_data.items())[:2]: # Keep it brief
                        prompt += f"    - {key.replace('_', ' ').title()}: {value}\n"

        prompt += "\nBased on the current situation, what is your next move or statement?"
        return prompt

    def score_turn(self):
        """
        Scores the current turn using the LLM.
        """
        if not self.scorecard:
            return

        print("\n--- Scoring Turn ---")
        scoring_prompt = self.generate_scoring_prompt()
        if not scoring_prompt:
            print("No scoring parameters found in the scenario. Skipping scoring.")
            return

        print("Getting scores from LLM...")
        scores_str = self.scorer_llm_provider.get_response("scorer", scoring_prompt)
        print(f"LLM Scores: {scores_str}")

        try:
            llm_scores = json.loads(scores_str)
            self.scorecard.update(llm_scores)
        except (json.JSONDecodeError, TypeError):
            print("Error: Could not decode scores from LLM response.")

    def generate_scoring_prompt(self):
        """
        Generates a prompt for the LLM to score the players.
        """
        scenario = self.scenario
        scoring_params = scenario.get("scoring_parameters")
        if not scoring_params:
            return None

        prompt = "You are an impartial judge. Based on the history of actions below, please score each player on the following criteria:\n"
        for score_name, config in scoring_params.items():
            prompt += f"  - {score_name}: {config.get('prompt', '')}\n"

        player_names = [p["controls"] for p in self.scenario.get("players", [])]
        prompt += f"\nPlease return the scores for the players: {', '.join(player_names)}.\n"

        prompt += "\nReturn the scores in a JSON format, like this: {\"player_name\": {\"score1\": value, \"score2\": value}}.\n"

        prompt += "\n--- History of Actions ---\n"
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
            "scenario": self.scenario,
            "history": self.history,
            "scorecard": self.scorecard.data if self.scorecard else {}
        }
        with open(save_path, 'w') as f:
            json.dump(game_state, f, indent=2)

    def load_game(self, save_path):
        """
        Loads a game state from a file.

        :param save_path: The path to the save file.
        """
        with open(save_path, 'r') as f:
            game_state = json.load(f)

        self.turn = game_state["turn"]
        self.scenario = game_state["scenario"]
        self.history = game_state["history"]

        if "scorecard" in self.scenario:
            self.scorecard = Scorecard(self.scenario)
            self.scorecard.data = game_state.get("scorecard", {})
        else:
            self.scorecard = None
