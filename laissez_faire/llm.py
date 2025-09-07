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
        Gets a response from the OpenAI API.
        """
        if not self.api_key:
            raise ValueError("API key is required for OpenAI model.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo", # Or any other model
            "messages": [{"role": "user", "content": prompt}]
        }

        # This is a basic implementation. In a real scenario, you'd
        # want to handle errors, timeouts, etc.
        # The requests library is already in requirements.txt
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status() # Raise an exception for bad status codes

        return response.json()["choices"][0]["message"]["content"]
