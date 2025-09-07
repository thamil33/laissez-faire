# Laissez-faire

<p align="center">
  <img src="lf.png" alt="Laissez-faire" width="500"/>
</p>

## An Infinite Grand Strategy Simulation Engine

Welcome to **Laissez-faire**, a 0-to-infinite player grand strategy simulation engine. Inspired by Paradox Interactive titles like *Europa Universalis*, this project provides a framework for creating simulations of limitless depth and complexity, bounded only by the computational power you provide.

What do we mean by "0-to-infinite player?" At its core, Laissez-faire is a simulation engine. It can run with zero human players, allowing you to observe complex systems and emergent behaviors. It can also support one or more human players, or even a multitude of AI-driven actors, creating a dynamic and unpredictable world. The number of entities, factions, and actors is not fixed, allowing for scenarios of ever-increasing scale.

Laissez-faire can be experienced in two ways:

1.  **As a standalone, terminal-based game:** For those who enjoy a classic, text-based experience.
2.  **As a powerful backend engine:** For developers who want to build their own games and simulations with custom GUIs and logic.

## The Vision: A Universe in a Box

The ultimate goal of Laissez-faire is to be a "universe in a box"—a tool for creating and exploring complex, dynamic worlds. The engine is designed to be highly flexible and extensible, making it suitable for a wide range of applications:

*   **Grand Strategy Games:** Build the next great historical, sci-fi, or fantasy grand strategy game.
*   **Educational Tools:** Simulate historical events, economic systems, or political processes.
*   **Research:** Explore complex systems, emergent behavior, and artificial intelligence.
*   **Storytelling:** Create dynamic, procedurally generated narratives and worlds.

## Key Features

*   **LLM-Powered Decision Making:** The game is driven by Large Language Models (LLMs) that control the actions of non-player characters, creating a challenging and unpredictable experience. The engine supports multiple backends, including OpenAI, OpenRouter, and local models run via Ollama or LM Studio.
*   **Flexible Scenarios:** Scenarios are defined in JSON files, making it easy to create and share your own custom games. See the [Scenario Creation Guide](docs/scenarios.md) for more details.
*   **Flexible Scorecards:** The engine features a flexible scorecard system that can be customized for each scenario. Scorecards can be text-based for display in the terminal or JSON-based for integration with external GUIs.
*   **Save and Load:** The engine supports saving and loading game states, allowing you to continue your game later.
*   **Terminal-Based Interface:** The primary interface is a terminal UI that uses the `rich` library to display styled text and tables.
*   **Comprehensive Unit Tests:** The project has a suite of unit tests to ensure that the core components are working correctly.

## Getting Started

To get started with Laissez-faire, you will need to have Python 3.7+ installed.

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/laissez-faire.git
    cd laissez-faire
    ```

2.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure your LLM provider:**

    The game's LLM (Large Language Model) configuration is handled in the `config.json` file. This file centralizes your settings, such as API keys, model names, and server URLs, so you don't have to edit the game's scenario files directly.

    To get started, copy the example configuration file:

    ```bash
    cp config.example.json config.json
    ```

    Now, open `config.json` and edit it to match your setup. The file contains a dictionary of "providers." The game scenarios will reference these providers by name (e.g., `"openai"`, `"openrouter"`, `"ollama"`).

    **Example `config.json`:**
    ```json
    {
      "providers": {
        "openai": {
          "model": "openai",
          "model_name": "gpt-4",
          "api_key": "YOUR_OPENAI_API_KEY",
          "base_url": null
        },
        "openrouter": {
          "model": "openai",
          "model_name": "google/gemini-flash-1.5",
          "api_key": "YOUR_OPENROUTER_API_KEY",
          "base_url": "https://openrouter.ai/api/v1"
        },
        "ollama": {
          "model": "ollama",
          "model_name": "llama3",
          "api_key": "ollama",
          "base_url": "http://localhost:11434/v1"
        },
        "lm_studio": {
          "model": "openai",
          "model_name": "local-model",
          "api_key": "not-needed",
          "base_url": "http://localhost:1234/v1"
        }
      }
    }
    ```

    #### Connecting to OpenAI-Compatible Services

    Any service that provides an OpenAI-compatible API can be used. This includes **OpenRouter**, **Ollama**, and **LM Studio**.

    1.  **Set the `model` parameter**: This should be set to `"openai"` or `"ollama"` to use the correct logic in the game engine.
    2.  **Set the `model_name`**: Specify the exact model you want to use (e.g., `"google/gemini-flash-1.5"`, `"llama3"`).
    3.  **Set your `api_key`**: Add your API key for the service.
    4.  **Set the `base_url`**: Provide the server address for the API.

    Scenarios can now use `"llm_provider": "your_provider_name"` to have AI players use the specified model.

4.  **Run the game:**

    ```bash
    python main.py
    ```

## Scenarios

This engine supports multiple scenarios, which are defined in the `laissez-faire/scenarios` directory. You can switch scenarios by editing the `scenario_path` in `main.py`. The flexibility of the engine means you can create scenarios of any scale, from a simple debate to a galaxy-spanning empire.

Here are the included scenarios:

*   **Philosopher's Debate:** A philosophical debate between two historical figures.
*   **Cold War:** A simulation of the geopolitical tensions between the USA and the USSR.
*   **Modern Day USA:** A simulation of modern-day geopolitics.
*   **Space Exploration:** A space-based grand strategy game scenario designed for use with a graphical front-end.

For more information on creating your own scenarios, see the [Scenario Creation Guide](docs/scenarios.md).

## Scoring System

The scoring system is designed to be highly flexible, allowing for different methods of tracking progress in a scenario. The scoring logic is defined in the `scoring_parameters` object in the scenario's JSON file. Each key in this object represents a score to be tracked.

For each score, you must define a `type`, which determines how the score is updated at the end of each turn. There are two types of scoring:

*   **`absolute`**: The LLM is prompted to return the new absolute value for the score, which then replaces the old value. This is useful for scores that are categorical or when you want the LLM to have full control over the value.

    *Example:*
    ```json
    "scoring_parameters": {
      "political_stability": {
        "type": "absolute",
        "prompt": "Return the new political stability score (1-100) for each country."
      }
    }
    ```

*   **`calculated`**: The LLM is prompted to return one or more "judgements" (e.g., a delta or a multiplier), and the engine uses a `calculation` formula to compute the new score. This is useful for scores that change incrementally or based on a specific formula.

    The `calculation` string can use the following variables:
    *   `current_value`: The current value of the score.
    *   `llm_judgement`: The value returned by the LLM for this score.

    *Example (additive scoring):*
    ```json
    "scoring_parameters": {
      "influence": {
        "type": "calculated",
        "calculation": "current_value + llm_judgement",
        "prompt": "Return the change (delta) in influence for each player."
      }
    }
    ```

    *Example (multiplicative scoring):*
    ```json
    "scoring_parameters": {
      "users": {
        "type": "calculated",
        "calculation": "current_value * (1 + llm_judgement)",
        "prompt": "Return a user growth multiplier (e.g., 0.1 for 10% growth) for each company."
      }
    }
    ```

### Scorecard Rendering

The display of the scorecard is controlled by the `scorecard` object in the scenario's JSON file. It has two main properties:

*   `render_type`: Can be `text` for a terminal-based display or `json` for integration with a GUI.
*   `template`: For `text` render type, this is a string that can contain placeholders for scores, e.g., `{Player.score_name}`.

## Running the Tests

To run the unit tests, you will need to install `pytest`:

```bash
pip install pytest
```

Then, you can run the tests from the root of the project. You may need to set the `PYTHONPATH` to include the project's root directory:

```bash
export PYTHONPATH=.
pytest
```

## License

This project is licensed under the GPLv3 License. See the `LICENSE` file for details.
