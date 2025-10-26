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

    def display_scores(self, scorecard):
        """
        Displays the current scorecard.
        """
        if not scorecard:
            return

        # The scorecard.render() method will return a string,
        # which we can then print inside a panel.
        score_output = scorecard.render()
        self.console.print(Panel(score_output, title="Scorecard", border_style="green"))

    def wait_for_turn(self):
        """
        Waits for the user to press Enter to continue to the next turn.
        """
        input("Press Enter to continue to the next turn...")
