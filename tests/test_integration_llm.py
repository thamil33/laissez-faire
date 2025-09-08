import pytest
import os
from laissez_faire.llm import LLMProvider

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration

# Get the API key from environment variables
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# Define the models to be tested
MODELS_TO_TEST = [
    "deepseek/deepseek-chat-v3-0324",
    "google/gemini-2.0-flash-001",
]

@pytest.mark.skipif(not OPENROUTER_API_KEY, reason="OPENROUTER_API_KEY is not set")
@pytest.mark.parametrize("model_name", MODELS_TO_TEST)
def test_openrouter_llm_response(model_name):
    """
    Tests that the LLMProvider can get a response from various OpenRouter models.
    This is an integration test and requires a real API key.
    """
    provider = LLMProvider(
        model="openai",
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
