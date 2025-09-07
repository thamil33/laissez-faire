# Laissez Faire

## A Grand Strategy Game Engine

Welcome to **Laissez Faire**, a zero-to-one player grand strategy game engine inspired by Paradox Interactive titles like *Europa Universalis*. This project aims to create a flexible and powerful engine that can be used to simulate a wide range of scenarios, from modern warfare to historical events.

The core of Laissez Faire is a text-based interface that allows you to interact with the game using natural language. Instead of micromanaging units and resources, you will develop high-level strategies and see how they play out in a dynamic and realistic world.

## Key Features

*   **LLM-Powered Decision Making:** The game is driven by Large Language Models (LLMs) that control the actions of non-player characters, creating a challenging and unpredictable experience. The engine supports multiple backends, including OpenAI and local models.
*   **Flexible Scenarios:** Scenarios are defined in JSON files, making it easy to create and share your own custom games. See the [Scenario Creation Guide](docs/scenarios.md) for more details.
*   **Flexible Scorecards:** The engine features a flexible scorecard system that can be customized for each scenario. Scorecards can be text-based for display in the terminal or JSON-based for integration with external GUIs.
*   **Save and Load:** The engine supports saving and loading game states, allowing you to continue your game later.
*   **Terminal-Based Interface:** The primary interface is a terminal UI that uses the `rich` library to display styled text and tables.
*   **Comprehensive Unit Tests:** The project has a suite of unit tests to ensure that the core components are working correctly.

## Getting Started

To get started with Laissez Faire, you will need to have Python 3.7+ installed.

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

    Create a `config.json` file in the root of the project by copying the `config.example.json` file. Then, edit it to configure your desired LLM provider. For detailed instructions, see the [LLM Configuration Guide](docs/llm_configuration.md).

4.  **Run the game:**

    ```bash
    python main.py
    ```

## Scenarios

This engine supports multiple scenarios, which are defined in the `laissez_faire/scenarios` directory. You can switch scenarios by editing the `scenario_path` in `main.py`.

Here are the included scenarios:

*   **Philosopher's Debate:** A philosophical debate between two historical figures.
*   **Cold War:** A simulation of the geopolitical tensions between the USA and the USSR.
*   **Modern Day USA:** A simulation of modern-day geopolitics.
*   **Space Exploration:** A space-based grand strategy game scenario designed for use with a graphical front-end.

For more information on creating your own scenarios, see the [Scenario Creation Guide](docs/scenarios.md).

## Scorecards

The scorecard system is designed to be highly flexible. Each scenario can define its own scorecard format using a `scorecard` object in the scenario's JSON file.

There are two types of scorecards:

*   **`text`:**  Renders a text-based scorecard in the terminal. The template can be customized with placeholders for scores.
*   **`json`:** Outputs the scores in JSON format, which is ideal for integration with a graphical user interface (GUI).

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
