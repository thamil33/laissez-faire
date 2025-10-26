import json
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
import operator
from laissez_faire.llm import LLMProvider

class GameMasterState(TypedDict):
    """
    Represents the state of the GameMaster agent.
    """
    scoring_prompt: str
    tools: list
    llm_response: str
    is_valid: bool
    retries: int

class GameMaster:
    """
    A LangGraph agent that ensures the scorer LLM returns a valid JSON response.
    """

    def __init__(self, scorer_llm_provider: LLMProvider):
        self.scorer_llm_provider = scorer_llm_provider
        self.graph = self._build_graph()

    def _build_graph(self):
        """
        Builds the LangGraph for the GameMaster agent.
        """
        builder = StateGraph(GameMasterState)

        builder.add_node("get_scores", self._get_scores)
        builder.add_node("validate_scores", self._validate_scores)
        builder.add_node("retry", self._retry)

        builder.set_entry_point("get_scores")

        builder.add_conditional_edges(
            "validate_scores",
            self._check_validity,
            {
                "valid": END,
                "invalid": "retry"
            }
        )
        builder.add_edge("retry", "get_scores")

        return builder.compile(checkpointer=MemorySaver())

    def _get_scores(self, state: GameMasterState):
        """
        Gets the scores from the scorer LLM.
        """
        response = self.scorer_llm_provider.get_response(
            "scorer",
            state["scoring_prompt"],
            tools=state["tools"]
        )
        return {"llm_response": response}

    def _validate_scores(self, state: GameMasterState):
        """
        Validates the scores from the scorer LLM.
        """
        try:
            json.loads(state["llm_response"])
            return {"is_valid": True}
        except (json.JSONDecodeError, TypeError):
            return {"is_valid": False}

    def _retry(self, state: GameMasterState):
        """
        Handles retries if the scores are invalid.
        """
        retries = state.get("retries", 0) + 1
        if retries > 3:
            raise ValueError("LLM failed to return valid JSON after 3 retries.")

        return {
            "scoring_prompt": f"The previous response was not valid JSON. Please try again, ensuring your output is a single, valid JSON object.\n\n{state['scoring_prompt']}",
            "retries": retries
        }

    def _check_validity(self, state: GameMasterState):
        """
        Checks if the scores are valid and routes to the appropriate node.
        """
        return "valid" if state["is_valid"] else "invalid"

    def get_valid_scores(self, scoring_prompt: str, tools: list):
        """
        Runs the graph to get a valid JSON response from the scorer LLM.
        """
        thread = {"configurable": {"thread_id": "scorer_thread"}}
        initial_state = {
            "scoring_prompt": scoring_prompt,
            "tools": tools,
            "retries": 0
        }

        # The _get_scores method is not picklable, so we bind it to the graph here
        self.graph.nodes["get_scores"].func = self._get_scores

        final_state = self.graph.invoke(initial_state, thread)
        return final_state["llm_response"]
