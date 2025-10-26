import pytest
import os
import json
from laissez_faire.llm import LLMProvider
from laissez_faire.engine import GameEngine

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration

# Get the API key from environment variables
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# Define the models to be tested
MODELS_TO_TEST = [
    "minimax/minimax-m2:free",
    "z-ai/glm-4.5-air:free"
]

@pytest.mark.skipif(not OPENROUTER_API_KEY, reason="OPENROUTER_API_KEY is not set")
@pytest.mark.parametrize("model_name", MODELS_TO_TEST)
def test_openrouter_llm_response(model_name):
    """
    Tests that the LLMProvider can get a response from various OpenRouter models.
    This is an integration test and requires a real API key.
    """
    provider = LLMProvider(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        model_name=model_name
    )

    prompt = "Hello, what is the capital of France?"
    response = provider.get_response("test_player", prompt)

    assert isinstance(response, str)
    assert "Error" not in response
    assert len(response) > 0
    # A simple check to see if the response is reasonable
    assert "Paris" in response

@pytest.mark.skipif(not OPENROUTER_API_KEY, reason="OPENROUTER_API_KEY is not set")
@pytest.mark.parametrize("model_name", MODELS_TO_TEST)
def test_gameplay_integration_with_openrouter(model_name):
    """
    Tests the gameplay loop with a real OpenRouter model.
    This test runs a simple scenario and checks that the scorecard is updated.
    """
    # Create the LLM providers for the players and the scorer
    player_provider = LLMProvider(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        model_name=model_name
    )
    scorer_provider = LLMProvider(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        model_name=model_name
    )

    llm_providers = {"Plato": player_provider, "Aristotle": player_provider}

    # Create a temporary scenario file for the test
    scenario_data = {
      "name": "Test Scenario: Philosopher's Debate",
      "description": "A simple debate between two philosophers on the nature of reality.",
      "player_entity_key": "philosophers",
      "players": [
        {
          "name": "Plato",
          "type": "ai",
          "controls": "Plato",
          "system_prompt": "You are the philosopher Plato. You believe that the physical world is not the real world; instead, it is a shadow of the world of Forms. Your goal is to convince your opponent of this."
        },
        {
          "name": "Aristotle",
          "type": "ai",
          "controls": "Aristotle",
          "system_prompt": "You are the philosopher Aristotle. You believe that the physical world is the real world, and that reality is perceived through the senses. Your goal is to convince your opponent of this."
        }
      ],
      "philosophers": {
        "Plato": {
          "coherence": 0
        },
        "Aristotle": {
          "coherence": 0
        }
      },
      "scoring_parameters": {
        "coherence": {
          "type": "calculated",
          "calculation": "current_value + llm_judgement",
          "prompt": "On a scale of 1-10, how coherent was the argument presented by each philosopher?",
          "tool_schema": {
            "type": "integer",
            "description": "A coherence score from 1 to 10."
          }
        }
      },
      "scorecard": {
        "render_type": "json"
      }
    }
    scenario_path = "test_scenario.json"
    with open(scenario_path, "w") as f:
        json.dump(scenario_data, f)

    # Load engine settings from config.json
    engine_settings = {}
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
            engine_settings = config.get("engine_settings", {})

    # Initialize the game engine
    engine = GameEngine(llm_providers, scorer_provider, scenario_path, engine_settings=engine_settings)

    try:
        # Run the game for one turn
        engine.run(max_turns=1)

        # Assert that the scorecard has been updated
        assert engine.scorecard is not None
        assert "Plato" in engine.scorecard.data
        assert "Aristotle" in engine.scorecard.data
        assert "coherence" in engine.scorecard.data["Plato"]
        assert "coherence" in engine.scorecard.data["Aristotle"]

        # Since the LLM's response is not deterministic, we can't assert a specific value.
        # Instead, we check that the score is not the initial value (0).
        assert engine.scorecard.data["Plato"]["coherence"] != 0
        assert engine.scorecard.data["Aristotle"]["coherence"] != 0
    finally:
        # Clean up the temporary scenario file
        os.remove(scenario_path)
