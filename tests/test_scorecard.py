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
