# === Extracted from section: 5.1. Code Dependency: Defining the Graph's Helper Logic ===
from langchain_core.messages import HumanMessage, RemoveMessage
from langgraph.prebuilt import tools_condition
from src.state import AgentState

class ConditionalLogic:
    def __init__(self, max_debate_rounds=1, max_risk_discuss_rounds=1):
        self.max_debate_rounds = max_debate_rounds
        self.max_risk_discuss_rounds = max_risk_discuss_rounds

    def should_continue_analyst(self, state: AgentState):
        # If the last message in the state is a tool call, route to the 'tools' node
        # Otherwise, the analyst is done, and we can continue.
        return "tools" if tools_condition(state) == "tools" else "continue"

    def should_continue_debate(self, state: AgentState) -> str:
        # If the debate has reached its maximum rounds, route to the manager.
        if state["investment_debate_state"]["count"] >= 2 * self.max_debate_rounds:
            return "Research Manager"
        # Otherwise, continue the debate by alternating speakers.
        return "Bear Researcher" if state["investment_debate_state"]["current_response"].startswith("Bull") else "Bull Researcher"

    def should_continue_risk_analysis(self, state: AgentState) -> str:
        # If the risk discussion has reached its maximum rounds, route to the judge.
        if state["risk_debate_state"]["count"] >= 3 * self.max_risk_discuss_rounds:
            return "Risk Judge"
        # Otherwise, continue the discussion by cycling through speakers.
        speaker = state["risk_debate_state"]["latest_speaker"]
        if speaker == "Risky Analyst": return "Safe Analyst"
        if speaker == "Safe Analyst": return "Neutral Analyst"
        return "Risky Analyst"

def create_msg_delete():
    # Helper function to clear messages from the state. This is useful to prevent
    # the context from one analyst from leaking into the next analyst's prompt.
    def delete_messages(state):
        return {"messages": [RemoveMessage(id=m.id) for m in state["messages"]] + [HumanMessage(content="Continue")]}
    return delete_messages

# Note: config will be imported from the calling module
# conditional_logic = ConditionalLogic(
#     max_debate_rounds=config['max_debate_rounds'],
#     max_risk_discuss_rounds=config['max_risk_discuss_rounds']
# )
conditional_logic = ConditionalLogic()
msg_clear_node = create_msg_delete()

print("Graph helper logic defined successfully.")
