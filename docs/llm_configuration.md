# LLM Configuration Guide

This guide explains how to configure the `config.json` file to connect to different Large Language Model (LLM) providers.

The `config.json` file in the root of the project allows you to specify which LLM provider to use, along with the necessary credentials and settings.

## Configuration Structure

The `llm_provider` section of the `config.json` file has the following structure:

```json
{
  "llm_provider": {
    "model": "provider_name",
    "api_key": "YOUR_API_KEY",
    "base_url": "URL_FOR_LOCAL_MODELS"
  }
}
```

- `model`: The name of the provider. Supported values are `"local"`, `"openai"`, and `"ollama"`.
- `api_key`: Your API key for the service (required for `openai`).
- `base_url`: The base URL for the API. This is used for local models like Ollama or LM Studio.

## Supported Providers

### Local (Placeholder)

The `"local"` provider is a simple placeholder that returns a fixed response. It's useful for testing the game engine without connecting to a real LLM.

**Note:** The placeholder response is a simple string. Features that expect a JSON response from the LLM, such as the scoring system, will not work correctly with the local provider.

```json
{
  "llm_provider": {
    "model": "local",
    "api_key": null,
    "base_url": null
  }
}
```

### OpenAI

The `"openai"` provider connects to the OpenAI API or any OpenAI-compatible API (like LM Studio or Open Router).

**For OpenAI:**
- Set `model` to `"openai"`.
- Set `api_key` to your OpenAI API key.
- `base_url` can be omitted (it defaults to `https://api.openai.com/v1`).

```json
{
  "llm_provider": {
    "model": "openai",
    "api_key": "sk-...",
    "base_url": null
  }
}
```

**For LM Studio:**
- Run the local server in LM Studio.
- Set `model` to `"openai"`.
- `api_key` can be any string (it's not required by LM Studio, but the field must be present).
- Set `base_url` to the URL of your local server (e.g., `http://localhost:1234/v1`).

```json
{
  "llm_provider": {
    "model": "openai",
    "api_key": "not-needed",
    "base_url": "http://localhost:1234/v1"
  }
}
```

**For Open Router:**
- Set `model` to `"openai"`.
- Set `api_key` to your Open Router API key.
- Set `base_url` to `https://openrouter.ai/api/v1`.

```json
{
  "llm_provider": {
    "model": "openai",
    "api_key": "sk-or-...",
    "base_url": "https://openrouter.ai/api/v1"
  }
}
```

### Ollama

The `"ollama"` provider connects to a local Ollama instance.

- Make sure your Ollama server is running.
- Set `model` to `"ollama"`.
- `api_key` is not needed.
- `base_url` can be omitted if your server is at the default `http://localhost:11434`.

```json
{
  "llm_provider": {
    "model": "ollama",
    "api_key": null,
    "base_url": "http://localhost:11434"
  }
}
```
