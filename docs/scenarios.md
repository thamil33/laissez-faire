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

#### Function Calling for Scoring

To ensure reliable and structured scoring, the game engine uses a form of function calling with the scorer LLM. This is defined by the `tool_schema` object within each scoring parameter.

- `tool_schema`: (object) A JSON schema object that defines the expected output for the score. This is used to construct a "tool" that the LLM is instructed to call.
  - `type`: (string) The data type of the expected value (e.g., "integer", "string", "number").
  - `description`: (string) A description of the value to be returned.

**Example:**
```json
"propaganda_effectiveness": {
  "type": "calculated",
  "calculation": "current_value + llm_judgement",
  "prompt": "Assess the change in propaganda effectiveness for each superpower (from -10 to +10).",
  "tool_schema": {
    "type": "integer",
    "description": "The change in propaganda effectiveness, e.g. -5, 0, or +5."
  }
}
```

---

### The `scorecard` Object

The `scorecard` object controls how the scorecard is displayed at the end of each turn.

- `render_type`: (string) Can be `text` for a terminal-based display or `json` for integration with a GUI.
- `template`: (string) For `text` render type, this is a string that can contain placeholders for scores, e.g., `{Player.score_name}`.

#### Complex Scorecard Templates

The `text` renderer uses the `rich` library, which supports a simplified version of bbcode for styling. You can use this to add colors, styles, and even emojis to your scorecard.

- **Colors:** `[red]text[/red]`, `[bold blue]text[/bold blue]`
- **Styles:** `[bold]text[/bold]`, `[italic]text[/italic]`
- **Emojis:** `:emoji_name:` (e.g., `:globe_showing_americas:`)

**Example:**
```json
"scorecard": {
  "render_type": "text",
  "template": "[bold]Global Situation Report[/bold]\n\nDEFCON Level: [bold red]{USA.defcon_level}[/bold red]\n\n[cyan]USA[/cyan] Prestige: {USA.global_prestige}\n[magenta]USSR[/magenta] Prestige: {USSR.global_prestige}\n\n\n[bold]World Influence Map[/bold]\n:globe_showing_americas: = Neutral/Contested | :us: = USA Influence | :ru: = USSR Influence"
}
```

---

## Full Example: Cold War (Complex)

Here is the full JSON for the revised `cold_war.json` scenario, which demonstrates a more complex setup.

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
      "influence": 90,
      "global_prestige": 100,
      "propaganda_effectiveness": 0,
      "western_europe_influence": "USA",
      "eastern_europe_influence": "NEU",
      "asia_influence": "NEU",
      "africa_influence": "NEU",
      "south_america_influence": "USA",
      "defcon_level": 5
    },
    "USSR": {
      "alignment": "Eastern Bloc",
      "economic_stability": 0.6,
      "political_stability": 0.9,
      "military_strength": 0.8,
      "influence": 80,
      "global_prestige": 80,
      "propaganda_effectiveness": 0,
      "western_europe_influence": "NEU",
      "eastern_europe_influence": "USSR",
      "asia_influence": "NEU",
      "africa_influence": "NEU",
      "south_america_influence": "NEU",
      "defcon_level": 5
    }
  },
  "scoring_parameters": {
    "global_prestige": {
      "type": "absolute",
      "prompt": "Judge the current global prestige of each superpower on a scale of 1-200.",
      "tool_schema": {
        "type": "integer",
        "description": "The absolute global prestige score, from 1 to 200."
      }
    },
    "propaganda_effectiveness": {
      "type": "calculated",
      "calculation": "current_value + llm_judgement",
      "prompt": "Assess the change in propaganda effectiveness for each superpower (from -10 to +10).",
      "tool_schema": {
        "type": "integer",
        "description": "The change in propaganda effectiveness, e.g. -5, 0, or +5."
      }
    },
    "western_europe_influence": {
      "type": "absolute",
      "prompt": "Who has more influence in Western Europe? ('USA', 'USSR', or 'NEU')",
      "tool_schema": {
        "type": "string",
        "description": "'USA' if USA has more influence, 'USSR' if USSR has more, 'NEU' for neutral."
      }
    },
    "eastern_europe_influence": {
      "type": "absolute",
      "prompt": "Who has more influence in Eastern Europe? ('USA', 'USSR', or 'NEU')",
      "tool_schema": {
        "type": "string",
        "description": "'USA' if USA has more influence, 'USSR' if USSR has more, 'NEU' for neutral."
      }
    },
    "asia_influence": {
      "type": "absolute",
      "prompt": "Who has more influence in Asia? ('USA', 'USSR', or 'NEU')",
      "tool_schema": {
        "type": "string",
        "description": "'USA' if USA has more influence, 'USSR' if USSR has more, 'NEU' for neutral."
      }
    },
    "africa_influence": {
      "type": "absolute",
      "prompt": "Who has more influence in Africa? ('USA', 'USSR', or 'NEU')",
      "tool_schema": {
        "type": "string",
        "description": "'USA' if USA has more influence, 'USSR' if USSR has more, 'NEU' for neutral."
      }
    },
    "south_america_influence": {
        "type": "absolute",
        "prompt": "Who has more influence in South America? ('USA', 'USSR', or 'NEU')",
        "tool_schema": {
            "type": "string",
            "description": "'USA' if USA has more influence, 'USSR' if USSR has more, 'NEU' for neutral."
        }
    },
    "defcon_level": {
        "type": "absolute",
        "prompt": "Based on the actions this turn, what is the new DEFCON level for both players (5 is peace, 1 is imminent war)?",
        "tool_schema": {
            "type": "integer",
            "description": "The new DEFCON level, from 1 to 5."
        }
    }
  },
  "scorecard": {
    "render_type": "text",
    "template": "[bold]Global Situation Report[/bold]\n\nDEFCON Level: [bold red]{USA.defcon_level}[/bold red]\n\n[cyan]USA[/cyan] Prestige: {USA.global_prestige} | Propaganda: {USA.propaganda_effectiveness}\n[magenta]USSR[/magenta] Prestige: {USSR.global_prestige} | Propaganda: {USSR.propaganda_effectiveness}\n\n\n[bold]World Influence Map[/bold]\n[white]NEU[/white] = Neutral/Contested | [blue]USA[/blue] = USA Influence | [red]USSR[/red] = USSR Influence\n\n      /`'-.      _/`.-'\\\n     /     `'--...--'`     \\\n    /  SA:{USA.south_america_influence}   WE:{USA.western_europe_influence} EE:{USSR.eastern_europe_influence}  \\\n   /                         \\\n  /      Asia:{USA.asia_influence}               \\\n |                           |\n |      Africa:{USA.africa_influence}            |\n |                           |\n  \\                         /\n   `'-.,_______________,.-'`"
  }
}
```
