import openai


class LLMProvider:
    """
    A provider for interacting with a Large Language Model, with support for
    conversation history.
    """

    def __init__(self, model="local", api_key=None, base_url=None, max_history_length=10, model_name="gpt-3.5-turbo"):
        """
        Initializes the LLM provider.

        :param model: The provider to use (e.g., 'local', 'openai', 'ollama').
        :param api_key: The API key for the LLM service.
        :param base_url: The base URL for the LLM service (for local models).
        :param max_history_length: The maximum number of messages to keep in the history.
        :param model_name: The specific model to use (e.g., 'gpt-3.5-turbo').
        """
        self.model = model
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.histories = {}
        self.max_history_length = max_history_length

    def get_or_create_history(self, player_name, system_prompt=None):
        """
        Retrieves or creates a conversation history for a player.

        :param player_name: The name of the player.
        :param system_prompt: An optional system prompt to initialize the history.
        :return: The conversation history (a list of messages).
        """
        if player_name not in self.histories:
            self.histories[player_name] = []
            if system_prompt:
                self.histories[player_name].append({"role": "system", "content": system_prompt})
        return self.histories[player_name]

    def get_response(self, player_name, prompt):
        """
        Gets a response from the LLM, maintaining conversation history.

        :param player_name: The name of the player to associate with the history.
        :param prompt: The prompt to send to the LLM.
        :return: The LLM's response as a string.
        """
        history = self.get_or_create_history(player_name)

        # Summarize history if it's too long, before adding the new prompt
        self.summarize_history(player_name)
        history = self.get_or_create_history(player_name)

        history.append({"role": "user", "content": prompt})

        if self.model == "local":
            response_content = self._get_response_local(history)
        elif self.model == "openai":
            response_content = self._get_response_openai(history)
        else:
            raise ValueError(f"Unsupported LLM model: {self.model}")

        history.append({"role": "assistant", "content": response_content})
        return response_content

    def summarize_history(self, player_name):
        """
        Summarizes the history for a player if it exceeds the max length.
        """
        history = self.histories.get(player_name, [])
        if len(history) > self.max_history_length:
            print(f"Summarizing history for {player_name}...")

            # Find the system prompt and keep it
            system_prompt = None
            if history and history[0]["role"] == "system":
                system_prompt = history.pop(0)

            # Create the summarization prompt
            summarization_prompt = (
                "Please summarize the following conversation. "
                "The summary should be concise and capture the key decisions and outcomes."
            )

            # Get the summary
            summary = self._get_response_openai([
                {"role": "system", "content": summarization_prompt},
                {"role": "user", "content": "\n".join([f"{m['role']}: {m['content']}" for m in history])}
            ])

            # Replace the history with the summary
            self.histories[player_name] = []
            if system_prompt:
                self.histories[player_name].append(system_prompt)
            self.histories[player_name].append({"role": "system", "content": f"Summary of previous events: {summary}"})

    def _get_response_local(self, messages):
        """
        Gets a placeholder response from a local model. This is used as a
        fallback when a proper LLM provider is not configured, allowing the
        application to run without requiring an API key.
        """
        print(f"Sending messages to local model: {messages}")
        return "This is a placeholder response from the local LLM."

    def _get_response_openai(self, messages):
        """
        Gets a response from an OpenAI-compatible API, using conversation history.
        """
        if not self.api_key:
            raise ValueError("API key is required for OpenAI-compatible models.")

        client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )

        return response.choices[0].message.content
