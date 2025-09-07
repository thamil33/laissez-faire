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

    def load_scenario(self, scenario_path):
        """
        Loads a scenario from a JSON file.

        :param scenario_path: The path to the scenario JSON file.
        :return: The scenario data as a dictionary.
        """
        with open(scenario_path, 'r') as f:
            return json.load(f)

    def run(self):
        """
        Runs the main game loop.
        """
        print("Game engine is running...")
        print(f"Loaded scenario: {self.scenario['name']}")
