# LLM Configuration Guide

This guide explains how to configure the `config.json` file to connect to different Large Language Model (LLM) providers.

## The `config.json` File

The `config.json` file in the root of the project is the central place to manage your LLM connections. It allows you to define a set of "providers" that can then be used by the game's scenarios. This approach keeps your personal API keys and server addresses separate from the scenario definitions.

To start, copy the example file:
```bash
cp config.example.json config.json
```

### Configuration Structure

The `config.json` file contains a single `providers` object. Each key inside this object is the name of a provider that you can reference in a scenario file.

Here is the structure of the default `config.json`:

```json
{
  "providers": {
    "openai": {
      "model_name": "gpt-4",
      "api_key": "YOUR_OPENAI_API_KEY",
      "base_url": null
    },
    "openrouter": {
      "model_name": "google/gemini-flash-1.5",
      "api_key": "YOUR_OPENROUTER_API_KEY",
      "base_url": "https://openrouter.ai/api/v1"
    },
    "lm_studio": {
      "model_name": "local-model",
      "api_key": "not-needed",
      "base_url": "http://localhost:1234/v1"
    }
  }
}
```

Each provider configuration has three potential fields:
- `model_name`: The specific model identifier for the API (e.g., `gpt-4`, `google/gemini-flash-1.5`).
- `api_key`: Your API key for the service.
- `base_url`: The base URL for the API, used for local models or custom endpoints.

## Connecting to Services

Any service that provides an OpenAI-compatible API can be used. This includes **OpenAI**, **OpenRouter**, and **LM Studio**.

1.  **Create a provider entry**: In `config.json`, create a new entry under `providers` (e.g., `"my_provider"`).
2.  **Set the `model_name`**: Specify the exact model you want to use (e.g., `"google/gemini-flash-1.5"`).
3.  **Set your `api_key`**: Add your API key for the service.
4.  **Set the `base_url`**: Provide the server address for the API.

## How Scenarios Use Providers

Scenario files in the `laissez-faire/scenarios/` directory determine which provider each AI player uses. This is done via the `llm_provider` key.

For example, in `cold_war.json`, you could have one player use OpenRouter and the other use a local model from LM Studio:

```json
"players": [
  {
    "name": "President of the United States",
    "type": "ai",
    "controls": "USA",
    "llm_provider": "openrouter"
    ...
  },
  {
    "name": "General Secretary of the Soviet Union",
    "type": "ai",
    "controls": "USSR",
    "llm_provider": "lm_studio"
    ...
  }
],
"scorer_llm_provider": "openai"
```

When the game starts, it will look up the `"openrouter"`, `"lm_studio"`, and `"openai"` providers in your `config.json` to get the necessary connection details.
