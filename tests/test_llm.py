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

@patch('openai.OpenAI')
def test_get_response_openai_api_error(mock_openai_class):
    """
    Tests how the OpenAI provider handles an API error.
    """
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.side_effect = Exception("API Error")
    mock_openai_class.return_value = mock_instance

    provider = LLMProvider(model="openai", api_key="test_key")

    with pytest.raises(Exception, match="API Error"):
        provider.get_response("player1", "test prompt")

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

@patch('openai.OpenAI')
def test_summarize_history(mock_openai_class):
    """
    Tests that the history summarization is triggered and works correctly.
    """
    api_key = "test_api_key"
    player_name = "player1"
    system_prompt = "You are a helpful assistant."
    summarization_response = "This is a summary."

    # Mock the response from the openai library
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = summarization_response

    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_instance

    provider = LLMProvider(model="openai", api_key=api_key, max_history_length=3)
    provider.get_or_create_history(player_name, system_prompt)

    # Add messages to exceed the history length
    for i in range(4):
        provider.get_response(player_name, f"message {i}")

    # Check that the history was summarized
    history = provider.histories[player_name]
    assert len(history) == 4
    assert "Summary of previous events" in provider.histories[player_name][1]['content']
    assert mock_instance.chat.completions.create.call_count == 6
