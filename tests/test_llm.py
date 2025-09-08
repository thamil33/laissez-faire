import pytest
from unittest.mock import patch, MagicMock
from laissez_faire.llm import LLMProvider

def test_llm_provider_init():
    """
    Tests that the LLMProvider can be initialized.
    """
    provider = LLMProvider()
    assert provider.model == "local"

    provider_openai = LLMProvider(model="openai", api_key="test_key")
    assert provider_openai.model == "openai"
    assert provider_openai.api_key == "test_key"

def test_llm_provider_get_response_local():
    """
    Tests that the local LLM provider returns a placeholder response.
    """
    provider = LLMProvider()
    response = provider.get_response("player1", "test prompt")
    assert isinstance(response, str)
    assert "placeholder" in response

@patch('openai.OpenAI')
def test_get_response_openai_success(mock_openai_class):
    """
    Tests the OpenAI provider with a mocked successful response.
    """
    api_key = "test_api_key"
    prompt = "Hello, world!"
    player_name = "player1"
    expected_response = "This is a test response from OpenAI."

    # Mock the response from the openai library
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = expected_response

    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_instance

    provider = LLMProvider(model="openai", api_key=api_key)
    response = provider.get_response(player_name, prompt)

    assert response == expected_response
    mock_openai_class.assert_called_once_with(api_key=api_key, base_url=None)
    mock_instance.chat.completions.create.assert_called_once()

def test_get_response_openai_no_api_key():
    """
    Tests that a ValueError is raised if the API key is missing for OpenAI.
    """
    provider = LLMProvider(model="openai")
    with pytest.raises(ValueError, match="API key is required for OpenAI-compatible models."):
        provider.get_response("player1", "test prompt")

@patch("openai.OpenAI")
def test_get_response_openai_api_error_silent_fail(mock_openai_class):
    """
    Tests that the OpenAI provider handles an API error gracefully.
    """
    # To trigger the error, we need to import the exception class
    from openai import APIError

    mock_instance = MagicMock()
    mock_instance.chat.completions.create.side_effect = APIError(
        "API Error", request=None, body=None
    )
    mock_openai_class.return_value = mock_instance

    provider = LLMProvider(model="openai", api_key="test_key")
    response = provider.get_response("player1", "test prompt")

    assert "Error: Could not get a response from the model." in response

def test_unsupported_model():
    """
    Tests that a ValueError is raised for an unsupported model.
    """
    provider = LLMProvider(model="unsupported_model")
    with pytest.raises(ValueError, match="Unsupported LLM model: unsupported_model"):
        provider.get_response("player1", "test prompt")

def test_get_or_create_history():
    """
    Tests that a conversation history can be retrieved or created.
    """
    provider = LLMProvider()
    history = provider.get_or_create_history("player1", "system prompt")
    assert history == [{"role": "system", "content": "system prompt"}]

    history2 = provider.get_or_create_history("player1")
    assert history2 == history

def test_get_or_create_history_no_prompt():
    """
    Tests that a conversation history can be created without a system prompt.
    """
    provider = LLMProvider()
    history = provider.get_or_create_history("player2")
    assert history == []

@patch('laissez_faire.llm.LLMProvider')
def test_history_summarization_is_triggered(mock_llm_provider):
    """
    Tests that the history summarization is triggered when the history
    exceeds the maximum length.
    """
    # Create a provider with a short history length
    provider = LLMProvider(max_history_length=3)
    provider.summarizer_provider = mock_llm_provider

    # Add messages to the history to exceed the max length
    provider.histories["player1"] = [
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": "message 1"},
        {"role": "assistant", "content": "response 1"},
        {"role": "user", "content": "message 2"},
        {"role": "assistant", "content": "response 2"},
    ]

    # Summarize the history
    provider.summarize_history("player1")

    # Check that the summarizer was called
    mock_llm_provider.get_response.assert_called_once()


@patch('laissez_faire.llm.LLMProvider')
def test_history_is_not_summarized_when_not_needed(mock_llm_provider):
    """
    Tests that the history is not summarized when it is not needed.
    """
    # Create a provider with a short history length
    provider = LLMProvider(max_history_length=5)
    provider.summarizer_provider = mock_llm_provider

    # Add messages to the history that do not exceed the max length
    provider.histories["player1"] = [
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": "message 1"},
        {"role": "assistant", "content": "response 1"},
    ]

    # Summarize the history
    provider.summarize_history("player1")

    # Check that the summarizer was not called
    mock_llm_provider.get_response.assert_not_called()
