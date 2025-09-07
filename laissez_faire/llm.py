import requests

class LLMProvider:
    """
    A provider for interacting with a Large Language Model.
    """

    def __init__(self, model="local", api_key=None, base_url=None):
        """
        Initializes the LLM provider.

        :param model: The model to use (e.g., 'local', 'openai', 'ollama').
        :param api_key: The API key for the LLM service.
        :param base_url: The base URL for the LLM service (for local models).
        """
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    def get_response(self, prompt):
        """
        Gets a response from the LLM.

        :param prompt: The prompt to send to the LLM.
        :return: The LLM's response as a string.
        """
        if self.model == "local":
            return self._get_response_local(prompt)
        elif self.model == "openai":
            return self._get_response_openai(prompt)
        elif self.model == "ollama":
            return self._get_response_ollama(prompt)
        # Add other models here as needed
        else:
            raise ValueError(f"Unsupported LLM model: {self.model}")

    def _get_response_local(self, prompt):
        """
        Gets a placeholder response from a local model.
        """
        print(f"Sending prompt to local model: {prompt}")
        return "This is a placeholder response from the local LLM."

    def _get_response_openai(self, prompt):
        """
        Gets a response from the OpenAI API or a compatible API.
        """
        if not self.api_key:
            raise ValueError("API key is required for OpenAI-compatible models.")

        base_url = self.base_url or "https://api.openai.com/v1"
        url = f"{base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo", # This should also be configurable
            "messages": [{"role": "user", "content": prompt}]
        }

        # This is a basic implementation. In a real scenario, you'd
        # want to handle errors, timeouts, etc.
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status() # Raise an exception for bad status codes

        return response.json()["choices"][0]["message"]["content"]

    def _get_response_ollama(self, prompt):
        """
        Gets a response from an Ollama model.
        """
        if not self.base_url:
            # Default for Ollama
            self.base_url = "http://localhost:11434"

        # Ollama uses a different API endpoint and request format
        url = f"{self.base_url}/api/generate"
        data = {
            "model": "llama2", # This should be configurable
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(url, json=data)
        response.raise_for_status()

        # For non-streaming, it's a single JSON object with a "response" key
        return response.json()["response"]
