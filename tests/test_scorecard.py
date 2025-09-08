import pytest
from laissez_faire.engine import Scorecard
import json

@pytest.fixture
def scenario_template():
    """A template for a scenario to test the scorecard."""
    return {
        "scorecard": {
            "render_type": "text",
            "template": "Player1 Score: {Player1.score}, Player2 Score: {Player2.score}"
        },
        "scoring_parameters": {
            "score": {
                "type": "calculated",
                "calculation": "current_value + llm_judgement"
            },
            "reputation": {
                "type": "calculated",
                "calculation": "current_value + llm_judgement"
            }
        }
    }

def test_scorecard_init(scenario_template):
    """Tests that the Scorecard can be initialized."""
    scorecard = Scorecard(scenario_template)
    assert scorecard.template == scenario_template["scorecard"]
    assert scorecard.data == {}

def test_scorecard_update_new_player(scenario_template):
    """Tests updating the scorecard with a new player."""
    scorecard = Scorecard(scenario_template)
    new_data = {"Player1": {"score": 10}}
    scorecard.update(new_data)
    assert scorecard.data == {"Player1": {"score": 10}}

def test_scorecard_update_existing_player(scenario_template):
    """Tests updating the scorecard with an existing player."""
    scorecard = Scorecard(scenario_template)
    scorecard.data = {"Player1": {"score": 10}}
    new_data = {"Player1": {"score": 5}}
    scorecard.update(new_data)
    assert scorecard.data == {"Player1": {"score": 15}}

def test_scorecard_update_multiple_scores(scenario_template):
    """Tests updating the scorecard with multiple scores for a player."""
    scorecard = Scorecard(scenario_template)
    scorecard.data = {"Player1": {"score": 10, "reputation": 5}}
    new_data = {"Player1": {"score": 5, "reputation": -2}}
    scorecard.update(new_data)
    assert scorecard.data == {"Player1": {"score": 15, "reputation": 3}}

def test_scorecard_render_text(scenario_template):
    """Tests rendering the scorecard with a text template."""
    scorecard = Scorecard(scenario_template)
    scorecard.data = {"Player1": {"score": 100}, "Player2": {"score": 50}}
    rendered = scorecard.render()
    assert rendered == "Player1 Score: 100, Player2 Score: 50"

def test_scorecard_render_missing_data(scenario_template):
    """Tests rendering when some data is missing."""
    scorecard = Scorecard(scenario_template)
    scorecard.data = {"Player1": {"score": 100}}
    rendered = scorecard.render()
    assert rendered == "Player1 Score: 100, Player2 Score: 0"

def test_scorecard_render_json():
    """Tests rendering the scorecard as JSON."""
    scenario = {"scorecard": {"render_type": "json"}}
    scorecard = Scorecard(scenario)
    scorecard.data = {"Player1": {"score": 100}, "Player2": {"score": 50}}
    rendered = scorecard.render()
    assert json.loads(rendered) == {"Player1": {"score": 100}, "Player2": {"score": 50}}

def test_scorecard_update_absolute_score(scenario_template):
    """Tests updating the scorecard with an absolute score type."""
    scenario_template["scoring_parameters"]["reputation"] = {"type": "absolute"}
    scorecard = Scorecard(scenario_template)
    scorecard.data = {"Player1": {"reputation": 5}}
    new_data = {"Player1": {"reputation": 10}}
    scorecard.update(new_data)
    assert scorecard.data == {"Player1": {"reputation": 10}}

def test_scorecard_update_complex_calculation(scenario_template):
    """Tests updating the scorecard with a more complex calculation."""
    scenario_template["scoring_parameters"]["score"] = {
        "type": "calculated",
        "calculation": "(current_value * 0.5) + llm_judgement"
    }
    scorecard = Scorecard(scenario_template)
    scorecard.data = {"Player1": {"score": 20}}
    new_data = {"Player1": {"score": 5}}
    scorecard.update(new_data)
    assert scorecard.data == {"Player1": {"score": 15.0}}

def test_scorecard_render_complex_template(scenario_template):
    """Tests rendering the scorecard with a more complex template."""
    scenario_template["scorecard"]["template"] = "Scores:\nPlayer1: {Player1.score}\nPlayer2: {Player2.score}\nPlayer1 again: {Player1.score}"
    scorecard = Scorecard(scenario_template)
    scorecard.data = {"Player1": {"score": 100}, "Player2": {"score": 50}}
    rendered = scorecard.render()
    assert rendered == "Scores:\nPlayer1: 100\nPlayer2: 50\nPlayer1 again: 100"

def test_safe_eval_invalid_expression_variable(scenario_template):
    """Tests that _safe_eval handles an invalid expression."""
    scorecard = Scorecard(scenario_template)
    with pytest.raises(ValueError, match="Invalid expression: unknown variable or number x"):
        scorecard._safe_eval("x + 1", {})

def test_safe_eval_invalid_expression_operator(scenario_template):
    """Tests that _safe_eval handles an invalid expression."""
    scorecard = Scorecard(scenario_template)
    with pytest.raises(ValueError, match="Invalid expression: unknown variable or number y"):
        scorecard._safe_eval("1 + y", {})

def test_safe_eval_unsupported_operator(scenario_template):
    """Tests that _safe_eval handles an unsupported operator."""
    scorecard = Scorecard(scenario_template)
    with pytest.raises(ValueError, match=r"Unsupported operator: %"):
        scorecard._safe_eval("1 % 2", {})

def test_scorecard_update_missing_config(scenario_template):
    """Tests updating the scorecard with a missing configuration."""
    scenario_template["scoring_parameters"] = {}
    scorecard = Scorecard(scenario_template)
    scorecard.data = {"Player1": {"score": 10}}
    new_data = {"Player1": {"score": 5}}
    scorecard.update(new_data)
    assert scorecard.data == {"Player1": {"score": 10}}

def test_scorecard_update_error_calculating_score(scenario_template, capsys):
    """Tests that an error is handled when calculating a score."""
    scenario_template["scoring_parameters"]["score"]["calculation"] = "current_value + x"
    scorecard = Scorecard(scenario_template)
    scorecard.data = {"Player1": {"score": 10}}
    new_data = {"Player1": {"score": 5}}
    scorecard.update(new_data)
    captured = capsys.readouterr()
    assert "Error calculating score for score" in captured.out
