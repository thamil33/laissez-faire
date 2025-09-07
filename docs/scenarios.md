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
- `scorer_llm_provider`: (string, optional) The LLM provider to use for scoring. If not provided, the engine will use the provider of the first player.
- `scorecard`: (object, optional) An object that defines how the scorecard is displayed.

---

### The `players` Object

Each player object in the `players` array has the following structure:

- `name`: (string) The name of the player or the persona they are playing.
- `type`: (string) The type of player. Can be `"human"` or `"ai"`.
- `controls`: (string) The key of the entity this player controls from the `[player_entity_key]` dictionary.
- `llm_provider`: (string, optional) The name of the LLM provider to use for this player (e.g., "openai", "ollama"). This must match a provider defined in your `config.json` file.
- `prompt_summary`: (string, optional) A brief summary of the player's objectives and personality. This is used in the game's UI.
- `system_prompt`: (string, optional) The system prompt that will be used to instruct the LLM for this player. This should provide detailed instructions on the player's goals, strategies, and personality.

**Example:**
```json
"players": [
  {
    "name": "President of the United States",
    "type": "ai",
    "controls": "USA",
    "llm_provider": "openai",
    "prompt_summary": "As the leader of the free world, you must champion democracy and capitalism while containing the spread of communism.",
    "system_prompt": "You are playing the role of the President of the United States in 1947..."
  }
]
```

---

### The `scoring_parameters` Object

The scoring system is designed to be highly flexible. The scoring logic is defined in the `scoring_parameters` object.

#### Simple Scoring

For simple scoring, `scoring_parameters` can be a dictionary where the key is the name of the score and the value is a description of what it means. The LLM will be asked to provide a new value for each score on each turn.

*Example:*
```json
"scoring_parameters": {
  "eloquence": "How well-articulated and persuasive the arguments are.",
  "originality": "How novel and insightful the ideas presented are."
}
```

#### Advanced Scoring

For more complex scoring, each score in `scoring_parameters` can be an object that defines how the score is calculated.

- `type`: (string) The type of scoring. Can be `absolute` or `calculated`.
- `calculation`: (string, required for `calculated` type) A formula for calculating the new score. It can use `current_value` and `llm_judgement`.
- `prompt`: (string) The prompt used to ask the LLM for its judgement.

**Example:**
```json
"scoring_parameters": {
  "influence_europe": {
    "type": "calculated",
    "calculation": "current_value + llm_judgement",
    "prompt": "Return the change (delta) in influence in Europe for each player."
  }
}
```

---

### The `scorecard` Object

The `scorecard` object controls how the scorecard is displayed at the end of each turn.

- `render_type`: (string) Can be `text` for a terminal-based display or `json` for integration with a GUI.
- `template`: (string) For `text` render type, this is a string that can contain placeholders for scores, e.g., `{Player.score_name}`.

**Example:**
```json
"scorecard": {
  "render_type": "text",
  "template": "World Influence Map:\n\nUSA Influence in Europe: {USA.influence_europe}"
}
```

---

## Full Example: Cold War

Here is the full JSON for the `cold_war.json` scenario, which you can use as a template.

```json
{
  "name": "The Cold War: A World Divided",
  "description": "A simulation of the geopolitical tensions between the United States and the Soviet Union in 1947, at the dawn of the Cold War.",
  "start_date": "1947-03-12",
  "player_entity_key": "countries",
  "players": [
    {
      "name": "President of the United States",
      "type": "ai",
      "controls": "USA",
      "llm_provider": "openai",
      "prompt_summary": "As the leader of the free world, you must champion democracy and capitalism while containing the spread of communism. Your goal is to build alliances, provide economic aid to allies, and maintain a strong military to deter Soviet aggression.",
      "system_prompt": "You are playing the role of the President of the United States in 1947. Your primary objective is to contain the global influence of the Soviet Union. You must use a combination of economic, political, and military strategies to achieve this. Key strategies include: 1. The Truman Doctrine: Provide political, military, and economic assistance to all democratic nations under threat from external or internal authoritarian forces. 2. The Marshall Plan: Offer economic aid to help rebuild Western European economies to create stable conditions in which democratic institutions could survive. 3. Covert Operations: Use intelligence agencies to support anti-communist factions and governments. Your personality should be resolute, confident, and statesmanlike. You must project strength and a commitment to democratic values."
    },
    {
      "name": "General Secretary of the Soviet Union",
      "type": "ai",
      "controls": "USSR",
      "llm_provider": "local",
      "prompt_summary": "As the leader of the global communist movement, you must protect the Soviet Union from capitalist encirclement and promote the spread of communism. Your goal is to expand your sphere of influence, support communist parties abroad, and develop your nation's industrial and military might.",
      "system_prompt": "You are playing the role of the General Secretary of the Soviet Union in 1947. Your primary objective is to expand the influence of communism and protect the USSR from the threat of capitalist aggression. You must use a combination of political, economic, and military strategies to achieve this. Key strategies include: 1. Cominform: Solidify Soviet influence over the communist parties of other countries and coordinate their policies. 2. Support for Liberation Movements: Provide aid and support to anti-colonial and communist movements around a wide range of issues. 4. Five-Year Plans: Focus on developing heavy industry and military technology to compete with the West. Your personality should be determined, secretive, and ideologically driven. You must project an image of unwavering strength and commitment to the communist cause."
    }
  ],
  "scorer_llm_provider": "ollama",
  "parameters": {
    "world_tension": 0.5,
    "nuclear_proliferation": 0.1
  },
  "countries": {
    "USA": {
      "alignment": "Western Bloc",
      "economic_stability": 0.9,
      "political_stability": 0.8,
      "military_strength": 0.7,
      "influence": 90
    },
    "USSR": {
      "alignment": "Eastern Bloc",
      "economic_stability": 0.6,
      "political_stability": 0.9,
      "military_strength": 0.8,
      "influence": 80
    }
  },
  "scoring_parameters": {
    "influence_europe": {
      "type": "calculated",
      "calculation": "current_value + llm_judgement",
      "prompt": "Return the change (delta) in influence in Europe for each player."
    }
  },
  "scorecard": {
    "render_type": "text",
    "template": "World Influence Map:\n\n      /`'-.      _/`.-'\\\n     /     `'--...--'`     \\\n    /                       \\\n   /     USA Influence       \\\n  /                           \\\n |     Europe: {USA.influence_europe}   Asia: {USA.influence_asia}    |\n |                           |\n |    Africa: {USA.influence_africa}      |\n |                           |\n |    USSR Influence         |\n |    Europe: {USSR.influence_europe}  Asia: {USSR.influence_asia}   |\n |   Africa: {USSR.influence_africa}       |\n  \\                         /\n   `'-.,_______________,.-'`"
  }
}
```
