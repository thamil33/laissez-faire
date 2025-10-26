import json
import re
import os
import operator

from .llm import LLMProvider
from .game_master import GameMaster

class Scorecard:
    """
    Manages the scorecard for the game.
    """
    def __init__(self, scenario):
        self.template = scenario.get("scorecard", {})
        self.scoring_parameters = scenario.get("scoring_parameters", {})
        self.data = {}
        self.scenario_parameters = scenario.get("parameters", {})
        self.turn_date = scenario.get("start_date")

    def _safe_eval(self, expr, context):
        """
        A safe evaluator for simple arithmetic and conditional expressions.
        """
        # Add scenario parameters and data to the context
        context['parameters'] = self.scenario_parameters
        context.update(self.data)

        # Allow access to player data, e.g. USA.influence
        for player, data in self.data.items():
            context[player] = data

        # Check for unsupported characters
        if re.search(r"[^a-zA-Z0-9\s_.,+\-*/()\"'\[\]={}]", expr):
            raise SyntaxError("Unsupported characters in expression.")

        # This is still not perfectly safe, but for this project, it's acceptable.
        # A better implementation would use an AST parser.
        return eval(expr, {"__builtins__": {}}, context)

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
                    except Exception as e:
                        print(f"Error calculating score for {score_name}: {e}")

    def _render_template(self, template):
        """
        Recursively renders a template, replacing placeholders.
        """
        if isinstance(template, str):
            # Handle simple placeholders like {USA.influence}
            placeholders = re.findall(r'\{([^}]+)\}', template)
            for placeholder in placeholders:
                try:
                    # Use safe_eval to get the value of the placeholder
                    value = self._safe_eval(placeholder, {})
                    template = template.replace(f'{{{placeholder}}}', str(value))
                except Exception as e:
                    # Fallback for simple placeholders that don't need eval
                    parts = placeholder.split('.')
                    if len(parts) == 2:
                        obj, key = parts
                        if obj == 'parameters':
                            value = self.scenario_parameters.get(key, f"Error: {key} not in parameters")
                        else:
                            value = self.data.get(obj, {}).get(key, 0)
                        template = template.replace(f'{{{placeholder}}}', str(value))
                    elif placeholder == 'turn_date':
                        template = template.replace(f'{{{placeholder}}}', str(self.turn_date))
                    else:
                        print(f"Error rendering placeholder '{placeholder}': {e}")
                        template = template.replace(f'{{{placeholder}}}', '[RENDER ERROR]')


            # Handle conditional placeholders like {{ 'a' if x > 0 else 'b' }}
            conditional_placeholders = re.findall(r'\{\{([^}]+)\}\}', template)
            for placeholder in conditional_placeholders:
                try:
                    value = self._safe_eval(placeholder, {})
                    template = template.replace(f'{{{{{placeholder}}}}}', str(value), 1)
                except Exception as e:
                    print(f"Error evaluating conditional placeholder: {e}")
                    template = template.replace(f'{{{{{placeholder}}}}}', '[EVALUATION ERROR]', 1)

            return template
        elif isinstance(template, dict):
            return {k: self._render_template(v) for k, v in template.items()}
        elif isinstance(template, list):
            return [self._render_template(i) for i in template]
        else:
            return template

    def render(self):
        """
        Renders the scorecard based on the template.
        """
        render_type = self.template.get("render_type", "text")
        template_content = self.template.get('template', '')

        rendered_content = self._render_template(template_content)

        if render_type == 'json':
            # The template is already a dict, so just dump it to a string
            return json.dumps(rendered_content, indent=2)
        else:
            # The template is a string
            return rendered_content

class GameEngine:
    """
    The main game engine for Laissez-faire.
    """

    def __init__(self, llm_providers: dict, scorer_llm_provider: LLMProvider, scenario_path=None, saves_dir="saves", engine_settings=None):
        """
        Initializes the game engine.
        :param llm_providers: A dictionary of LLM providers for each player.
        :param scorer_llm_provider: An LLM provider for the scorer.
        :param scenario_path: The path to the scenario JSON file (optional).
        :param engine_settings: A dictionary of engine settings.
        """
        self.scenario = self.load_scenario(scenario_path) if scenario_path else {}
        self.turn = 0
        self.llm_providers = llm_providers
        self.scorer_llm_provider = scorer_llm_provider
        self.history = []
        self.scorecard = None
        self.saves_dir = saves_dir
        self.engine_settings = engine_settings if engine_settings is not None else {}
        self.game_master = GameMaster(self.scorer_llm_provider)

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
                self.scorecard.turn_date = self.get_turn_date()
                ui.display_scores(self.scorecard)

            # Auto-save the game
            if not os.path.exists(self.saves_dir):
                os.makedirs(self.saves_dir)
            self.save_game(os.path.join(self.saves_dir, "autosave.json"))
            print("Game auto-saved.")

            if self.engine_settings.get("step_through_turns") and ui:
                ui.wait_for_turn()

        print("Game simulation finished.")

    def get_turn_date(self):
        from datetime import datetime, timedelta

        start_date_str = self.scenario.get("start_date", "2024-01-01")
        start_date = datetime.fromisoformat(start_date_str)
        # Assuming each turn is a month
        turn_date = start_date + timedelta(days=30 * self.turn)
        return turn_date.strftime("%Y-%m-%d")

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
        scoring_prompt, tools = self._generate_scoring_request()
        if not scoring_prompt:
            print("No scoring parameters found in the scenario. Skipping scoring.")
            return

        print("Getting scores from LLM...")
        if self.engine_settings.get("debug_mode"):
            print("\n--- Scoring LLM Call ---")
            print(f"Prompt: {scoring_prompt}")
            print(f"Tools: {json.dumps(tools, indent=2)}")
            print("------------------------\n")
        
        response_str = self.game_master.get_valid_scores(scoring_prompt, tools)
        print(f"LLM Scores: {response_str}")

        try:
            response_data = json.loads(response_str)
            llm_scores = response_data.get("scores", {})
            reasoning = response_data.get("reasoning", "No reasoning provided.")
            if self.engine_settings.get("debug_mode"):
                print(f"Reasoning: {reasoning}")
            self.scorecard.update(llm_scores)
        except (json.JSONDecodeError, TypeError):
            print("Error: Could not decode scores from LLM response.")
            if self.engine_settings.get("debug_mode"):
                print(f"Malformed JSON string: {response_str}")

    def _generate_scoring_request(self):
        """
        Generates a prompt and a tool schema for the LLM to score the players.
        """
        scenario = self.scenario
        scoring_params = scenario.get("scoring_parameters")
        if not scoring_params:
            return None, None

        # Generate the text prompt
        prompt = "You are an impartial judge. Based on the history of actions below, please provide a brief reasoning for your scoring decisions and then score each player on the following criteria:\n"
        for score_name, config in scoring_params.items():
            prompt += f"  - {score_name}: {config.get('prompt', '')}\n"
        prompt += "\n--- History of Actions ---\n"
        recent_history = [h for h in self.history if h['turn'] == self.turn]
        for event in recent_history:
            prompt += f"Turn {event['turn']}, {event['player']}: {event['action']}\n"

        # Generate the tool schema
        player_names = [p["controls"] for p in self.scenario.get("players", [])]
        player_properties = {}
        for player_name in player_names:
            score_properties = {}
            for score_name, config in scoring_params.items():
                if "tool_schema" in config:
                    score_properties[score_name] = config["tool_schema"]
            player_properties[player_name] = {
                "type": "object",
                "properties": score_properties
            }

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "record_scores",
                    "description": "Records the scores for all players.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "scores": {
                                "type": "object",
                                "properties": player_properties
                            },
                            "reasoning": {
                                "type": "string",
                                "description": "A brief explanation of the scoring decisions."
                            }
                        },
                        "required": ["scores", "reasoning"]
                    }
                }
            }
        ]

        return prompt, tools

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
