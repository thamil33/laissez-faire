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
    "local": {},
    "openai": {
      "model": "openai",
      "api_key": "YOUR_OPENAI_API_KEY",
      "base_url": null
    },
    "ollama": {
      "model": "ollama",
      "api_key": null,
      "base_url": "http://localhost:11434"
    },
    "lm_studio": {
      "model": "openai",
      "api_key": "not-needed",
      "base_url": "http://localhost:1234/v1"
    }
  }
}
```

Each provider configuration has three potential fields:
- `model`: The type of LLM backend. Supported values are `"local"`, `"openai"`, and `"ollama"`.
- `api_key`: Your API key for the service (required for `openai` and other compatible services like OpenRouter).
- `base_url`: The base URL for the API, used for local models or custom endpoints.

## Connecting to Local LLMs

### LM Studio

LM Studio exposes an OpenAI-compatible server.
1.  In LM Studio, navigate to the "Local Server" tab and start the server.
2.  In `config.json`, the `lm_studio` provider is already configured for the default LM Studio address (`http://localhost:1234/v1`). You can adjust the `base_url` if you have a custom setup. The `api_key` is not required by LM Studio, but the field should be present.
3.  In a scenario file, you can set `"llm_provider": "lm_studio"` for any AI player to use your LM Studio model.

### Ollama

1.  Ensure your local Ollama server is running.
2.  In `config.json`, the `ollama` provider is configured for the default address (`http://localhost:11434`). You can change the `base_url` if needed.
3.  In a scenario file, set `"llm_provider": "ollama"` for any AI player to use your Ollama model.

## Connecting to Cloud Services

### OpenAI

1.  In `config.json`, find the `openai` provider.
2.  Replace `"YOUR_OPENAI_API_KEY"` with your actual OpenAI API key.
3.  In a scenario file, set `"llm_provider": "openai"` to use the OpenAI API.

### OpenRouter (and other OpenAI-compatible services)

You can use the `openai` provider type to connect to any OpenAI-compatible API endpoint.

1.  You can either modify the existing `openai` provider or create a new one (e.g., `"openrouter"`).
2.  Set the `api_key` to your service's API key.
3.  Set the `base_url` to the service's API endpoint (e.g., `https://openrouter.ai/api/v1`).

Example for a new OpenRouter provider:
```json
"openrouter": {
  "model": "openai",
  "api_key": "sk-or-...",
  "base_url": "https://openrouter.ai/api/v1"
}
```

## How Scenarios Use Providers

Scenario files in the `laissez_faire/scenarios/` directory determine which provider each AI player uses. This is done via the `llm_provider` key.

For example, in `cold_war.json`, you could have one player use OpenAI and the other use a local model:

```json
"players": [
  {
    "name": "President of the United States",
    "type": "ai",
    "controls": "USA",
    "llm_provider": "openai"
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
"scorer_llm_provider": "ollama"
```

When the game starts, it will look up the `"openai"`, `"lm_studio"`, and `"ollama"` providers in your `config.json` to get the necessary connection details.
