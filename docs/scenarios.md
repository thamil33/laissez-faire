# Scenario Creation Guide

This guide explains how to create your own scenarios for the Laissez-faire game engine. Scenarios are defined in JSON files located in the `laissez_faire/scenarios/` directory.

## Scenario Structure

A scenario file is a JSON object with the following main keys:

- `name`: (string) The name of the scenario.
- `description`: (string) A brief description of the scenario's premise.
- `start_date`: (string) The starting date for the scenario.
- `player_entity_key`: (string) The key for the dictionary of entities that players control (e.g., "countries", "debaters").
- `players`: (array) A list of player objects.
- `[player_entity_key]`: (object) A dictionary of the entities in the game. The key for this object should match the value of `player_entity_key`.
- `parameters`: (object) A dictionary of global parameters for the scenario.
- `scoring_parameters`: (object) A dictionary defining the criteria for scoring.

### `players`

Each player object in the `players` array has the following structure:

- `name`: (string) The name of the player or the persona they are playing.
- `type`: (string) The type of player. Can be `"human"` or `"ai"`.
- `controls`: (string) The key of the entity this player controls from the `[player_entity_key]` dictionary.

**Example:**
```json
"players": [
  {
    "name": "Albert Einstein",
    "type": "ai",
    "controls": "Einstein"
  }
]
```

### `[player_entity_key]`

This is a dictionary where each key is an entity that can be controlled by a player. The value is an object containing the attributes of that entity.

**Example (`player_entity_key` is "debaters"):**
```json
"debaters": {
  "Einstein": {
    "field": "Theoretical Physics",
    "famous_for": "Theory of Relativity"
  },
  "Jobs": {
    "field": "Technology & Business",
    "famous_for": "Apple Inc., iPhone"
  }
}
```

### `parameters`

A dictionary of global parameters that provide context for the scenario. These are displayed to the LLM in the prompt.

**Example:**
```json
"parameters": {
  "topic": "The role of intuition versus rigorous analysis in driving true innovation."
}
```

### `scoring_parameters`

A dictionary defining the criteria on which the players will be scored by the LLM. The key is the name of the score, and the value is a description of what it means.

**Example:**
```json
"scoring_parameters": {
  "eloquence": "How well-articulated and persuasive the arguments are.",
  "originality": "How novel and insightful the ideas presented are."
}
```
## Example Scenario: Philosophical Debate

Here is the full JSON for the `philosophers_debate.json` scenario, which you can use as a template for creating your own scenarios.

```json
{
  "name": "A Debate of Minds",
  "description": "A philosophical debate between Albert Einstein and Steve Jobs on the nature of innovation and intuition.",
  "start_date": "2024-01-01",
  "player_entity_key": "debaters",
  "players": [
    {
      "name": "Albert Einstein",
      "type": "ai",
      "controls": "Einstein"
    },
    {
      "name": "Steve Jobs",
      "type": "ai",
      "controls": "Jobs"
    }
  ],
  "debaters": {
    "Einstein": {
      "field": "Theoretical Physics",
      "famous_for": "Theory of Relativity"
    },
    "Jobs": {
      "field": "Technology & Business",
      "famous_for": "Apple Inc., iPhone"
    }
  },
  "scoring_parameters": {
    "eloquence": "How well-articulated and persuasive the arguments are.",
    "originality": "How novel and insightful the ideas presented are.",
    "relevance": "How well the arguments stick to the topic of innovation and intuition.",
    "logic": "The strength and coherence of the reasoning."
  },
  "parameters": {
    "topic": "The role of intuition versus rigorous analysis in driving true innovation."
  }
}
```
