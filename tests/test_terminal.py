import pytest
from unittest.mock import MagicMock, patch
from laissez_faire.terminal import TerminalUI
from laissez_faire.engine import Scorecard

@pytest.fixture
def mock_console():
    """Fixture for a mock rich console."""
    return MagicMock()

@patch('laissez_faire.terminal.Console')
def test_terminal_ui_init(mock_console_class):
    """Tests that the TerminalUI initializes the console."""
    ui = TerminalUI()
    mock_console_class.assert_called_once()
    assert ui.console is not None

def test_display_welcome(mock_console):
    """Tests the display_welcome method."""
    ui = TerminalUI()
    ui.console = mock_console
    ui.display_welcome("Test Scenario")
    mock_console.print.assert_called_once()
    # Check that the panel contains the scenario name
    args, kwargs = mock_console.print.call_args
    assert "Test Scenario" in str(args[0].renderable)

def test_display_scenario_details(mock_console):
    """Tests the display_scenario_details method."""
    ui = TerminalUI()
    ui.console = mock_console
    scenario = {"name": "Test Scenario", "description": "A test scenario."}
    ui.display_scenario_details(scenario)
    mock_console.print.assert_called_once()
    # Check that the table contains scenario details
    args, kwargs = mock_console.print.call_args
    table = args[0]
    assert table.title == "Scenario Details"

    # To check the content, we can look at the calls to add_row
    # This is a bit of a hack, but it's hard to get the rendered content of a table
    # without a console.
    assert any("Test Scenario" in str(cell) for cell in table.columns[1]._cells)

def test_display_scores(mock_console):
    """Tests the display_scores method."""
    ui = TerminalUI()
    ui.console = mock_console

    # Create a mock scorecard that returns a specific string
    mock_scorecard = MagicMock(spec=Scorecard)
    mock_scorecard.render.return_value = "Player1: 100"

    ui.display_scores(mock_scorecard)

    mock_scorecard.render.assert_called_once()
    mock_console.print.assert_called_once()

    # Check that the panel contains the rendered scorecard
    args, kwargs = mock_console.print.call_args
    assert "Player1: 100" in str(args[0].renderable)

def test_display_scores_no_scorecard(mock_console):
    """Tests that display_scores handles a None scorecard."""
    ui = TerminalUI()
    ui.console = mock_console
    ui.display_scores(None)
    mock_console.print.assert_not_called()
