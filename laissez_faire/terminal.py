from rich.console import Console
from rich.panel import Panel
from rich.table import Table

class TerminalUI:
    """
    The terminal user interface for Laissez Faire.
    """

    def __init__(self):
        """
        Initializes the terminal UI.
        """
        self.console = Console()

    def display_welcome(self, scenario_name):
        """
        Displays a welcome message.

        :param scenario_name: The name of the loaded scenario.
        """
        self.console.print(Panel(f"Welcome to Laissez Faire!\nLoaded scenario: [bold green]{scenario_name}[/bold green]", title="Laissez Faire", border_style="blue"))

    def display_scenario_details(self, scenario):
        """
        Displays the details of a scenario.

        :param scenario: The scenario data.
        """
        table = Table(title="Scenario Details")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="magenta")

        for key, value in scenario.items():
            table.add_row(key, str(value))

        self.console.print(table)

    def display_scores(self, scores):
        """
        Displays the current scores in a table.
        """
        if not scores:
            return

        table = Table(title="Current Scores")

        # Get all unique score names
        score_names = set()
        for player_scores in scores.values():
            score_names.update(player_scores.keys())

        sorted_score_names = sorted(list(score_names))

        table.add_column("Player", justify="left")
        for score_name in sorted_score_names:
            table.add_column(score_name.replace('_', ' ').title(), justify="center")

        for player_name, player_scores in sorted(scores.items()):
            row = [player_name]
            for score_name in sorted_score_names:
                row.append(str(player_scores.get(score_name, 0)))
            table.add_row(*row)

        self.console.print(table)
