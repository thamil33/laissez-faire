import pytest
from unittest.mock import MagicMock
from laissez_faire.llm import LLMProvider

@pytest.fixture
def mock_llm_providers():
    """Fixture for a mock LLM providers dictionary."""
    return {"player1": MagicMock(spec=LLMProvider)}

@pytest.fixture
def mock_scorer_llm_provider():
    """Fixture for a mock scorer LLM provider."""
    return MagicMock(spec=LLMProvider)
