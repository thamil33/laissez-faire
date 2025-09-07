import pytest
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
