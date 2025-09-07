import pytest
from laissez_faire.engine import Scorecard

@pytest.fixture
def scorecard_template():
    """A template for testing the scorecard."""
    return {
        "type": "text",
        "template": "Player1 Score: {Player1.score}, Player2 Score: {Player2.score}"
    }

def test_scorecard_init(scorecard_template):
    """Tests that the Scorecard can be initialized."""
    scorecard = Scorecard(scorecard_template)
    assert scorecard.template == scorecard_template
    assert scorecard.data == {}

def test_scorecard_update_new_player():
    """Tests updating the scorecard with a new player."""
    scorecard = Scorecard({})
    new_data = {"Player1": {"score": 10}}
    scorecard.update(new_data)
    assert scorecard.data == {"Player1": {"score": 10}}

def test_scorecard_update_existing_player():
    """Tests updating the scorecard with an existing player."""
    scorecard = Scorecard({})
    scorecard.data = {"Player1": {"score": 10}}
    new_data = {"Player1": {"score": 5}}
    scorecard.update(new_data)
    assert scorecard.data == {"Player1": {"score": 15}}

def test_scorecard_update_multiple_scores():
    """Tests updating the scorecard with multiple scores for a player."""
    scorecard = Scorecard({})
    scorecard.data = {"Player1": {"score": 10, "reputation": 5}}
    new_data = {"Player1": {"score": 5, "reputation": -2}}
    scorecard.update(new_data)
    assert scorecard.data == {"Player1": {"score": 15, "reputation": 3}}

def test_scorecard_render_text(scorecard_template):
    """Tests rendering the scorecard with a text template."""
    scorecard = Scorecard(scorecard_template)
    scorecard.data = {"Player1": {"score": 100}, "Player2": {"score": 50}}
    rendered = scorecard.render()
    assert rendered == "Player1 Score: 100, Player2 Score: 50"

def test_scorecard_render_missing_data(scorecard_template):
    """Tests rendering when some data is missing."""
    scorecard = Scorecard(scorecard_template)
    scorecard.data = {"Player1": {"score": 100}}
    rendered = scorecard.render()
    assert rendered == "Player1 Score: 100, Player2 Score: 0"

def test_scorecard_render_json():
    """Tests rendering the scorecard as JSON."""
    scorecard = Scorecard({"type": "json"})
    scorecard.data = {"Player1": {"score": 100}, "Player2": {"score": 50}}
    rendered = scorecard.render()
    import json
    assert json.loads(rendered) == {"Player1": {"score": 100}, "Player2": {"score": 50}}
