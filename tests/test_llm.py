import pytest
import requests
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
    response = provider.get_response("test prompt")
    assert isinstance(response, str)
    assert "placeholder" in response

def test_get_response_openai_success(requests_mock):
    """
    Tests the OpenAI provider with a mocked successful response.
    """
    api_key = "test_api_key"
    prompt = "Hello, world!"
    expected_response = "This is a test response from OpenAI."

    # Mock the OpenAI API endpoint
    requests_mock.post("https://api.openai.com/v1/chat/completions", json={
        "choices": [{"message": {"content": expected_response}}]
    })

    provider = LLMProvider(model="openai", api_key=api_key)
    response = provider.get_response(prompt)

    assert response == expected_response
    assert requests_mock.called
    assert requests_mock.last_request.headers["Authorization"] == f"Bearer {api_key}"

def test_get_response_openai_custom_url(requests_mock):
    """
    Tests the OpenAI provider with a custom base URL.
    """
    api_key = "test_api_key"
    base_url = "https://api.example.com"
    prompt = "Test prompt"
    expected_response = "Custom URL response"

    requests_mock.post(f"{base_url}/chat/completions", json={
        "choices": [{"message": {"content": expected_response}}]
    })

    provider = LLMProvider(model="openai", api_key=api_key, base_url=base_url)
    response = provider.get_response(prompt)

    assert response == expected_response

def test_get_response_openai_no_api_key():
    """
    Tests that a ValueError is raised if the API key is missing for OpenAI.
    """
    provider = LLMProvider(model="openai")
    with pytest.raises(ValueError, match="API key is required"):
        provider.get_response("test prompt")

def test_get_response_openai_api_error(requests_mock):
    """
    Tests how the OpenAI provider handles an API error.
    """
    requests_mock.post("https://api.openai.com/v1/chat/completions", status_code=500)
    provider = LLMProvider(model="openai", api_key="test_key")

    with pytest.raises(requests.exceptions.HTTPError):
        provider.get_response("test prompt")

def test_get_response_ollama_success(requests_mock):
    """
    Tests the Ollama provider with a mocked successful response.
    """
    prompt = "Why is the sky blue?"
    expected_response = "Because of Rayleigh scattering."
    base_url = "http://localhost:11434"

    requests_mock.post(f"{base_url}/api/generate", json={
        "response": expected_response
    })

    provider = LLMProvider(model="ollama", base_url=base_url)
    response = provider.get_response(prompt)

    assert response == expected_response

def test_get_response_ollama_custom_url(requests_mock):
    """
    Tests the Ollama provider with a custom base URL.
    """
    base_url = "http://custom-ollama:1234"
    prompt = "Test prompt"
    expected_response = "Custom Ollama response"

    requests_mock.post(f"{base_url}/api/generate", json={"response": expected_response})

    provider = LLMProvider(model="ollama", base_url=base_url)
    response = provider.get_response(prompt)

    assert response == expected_response

def test_get_response_ollama_api_error(requests_mock):
    """
    Tests how the Ollama provider handles an API error.
    """
    base_url = "http://localhost:11434"
    requests_mock.post(f"{base_url}/api/generate", status_code=500)
    provider = LLMProvider(model="ollama", base_url=base_url)

    with pytest.raises(requests.exceptions.HTTPError):
        provider.get_response("test prompt")

def test_unsupported_model():
    """
    Tests that a ValueError is raised for an unsupported model.
    """
    provider = LLMProvider(model="unsupported_model")
    with pytest.raises(ValueError, match="Unsupported LLM model: unsupported_model"):
        provider.get_response("test prompt")
