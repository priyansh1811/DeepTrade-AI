# === Extracted from section: 5.3. Building the `StateGraph`: Wiring All Agents Together ===
from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.graph.nodes import *
from src.graph.helpers import conditional_logic, msg_clear_node
from src.agents.analyst import create_analyst_node, market_analyst_system_message, social_analyst_system_message, news_analyst_system_message, fundamentals_analyst_system_message
from src.agents.research import create_researcher_node, create_research_manager, bull_prompt, bear_prompt
from src.agents.trader_risk import create_trader, create_risk_debator, create_risk_manager, risky_prompt, safe_prompt, neutral_prompt

def build_graph():
    """Build and return the compiled graph with all nodes properly initialized."""
    # Import real LLMs if available
    from src.llms import deep_thinking_llm, quick_thinking_llm
    from langchain_core.language_models.base import BaseLanguageModel
    from langchain_core.messages import BaseMessage
    from typing import Any, List, Optional, Sequence
    
    # Create mock LLM as fallback
    class MockLLM(BaseLanguageModel):
        def _generate(self, messages: List[BaseMessage], **kwargs) -> Any:
            return type('obj', (object,), {'generations': [type('obj', (object,), {'text': 'Mock response', 'message': type('obj', (object,), {'content': 'Mock response', 'tool_calls': []})()})]})()
        
        def _llm_type(self) -> str:
            return "mock"
        
        def bind_tools(self, tools, **kwargs):
            return self
        
        def invoke(self, input, **kwargs):
            return type('obj', (object,), {'content': 'Mock response', 'tool_calls': []})()
        
        def predict(self, text, **kwargs):
            return "Mock response"
        
        def predict_messages(self, messages, **kwargs):
            return type('obj', (object,), {'content': 'Mock response', 'tool_calls': []})()
        
        def generate_prompt(self, prompt, **kwargs):
            return type('obj', (object,), {'generations': [type('obj', (object,), {'text': 'Mock response'})()]})()
        
        async def agenerate_prompt(self, prompt, **kwargs):
            return type('obj', (object,), {'generations': [type('obj', (object,), {'text': 'Mock response'})()]})()
        
        async def apredict(self, text, **kwargs):
            return "Mock response"
        
        async def apredict_messages(self, messages, **kwargs):
            return type('obj', (object,), {'content': 'Mock response', 'tool_calls': []})()
    
    class MockMemory:
        def get_memories(self, query): return []
    
    # Use real LLMs if available, otherwise use mock
    if deep_thinking_llm is not None and quick_thinking_llm is not None:
        print("Using real OpenAI LLMs")
        llm_deep = deep_thinking_llm
        llm_quick = quick_thinking_llm
    else:
        print("Using mock LLMs (API keys not configured)")
        llm_deep = MockLLM()
        llm_quick = MockLLM()
    
    mock_memory = MockMemory()
    
    # Create all the nodes
    market_analyst_node = create_analyst_node(llm_quick, None, market_analyst_system_message, [get_yfinance_data, get_technical_indicators], "market_report")
    social_analyst_node = create_analyst_node(llm_quick, None, social_analyst_system_message, [get_social_media_sentiment], "sentiment_report")
    news_analyst_node = create_analyst_node(llm_quick, None, news_analyst_system_message, [get_finnhub_news, get_macroeconomic_news], "news_report")
    fundamentals_analyst_node = create_analyst_node(llm_quick, None, fundamentals_analyst_system_message, [get_fundamental_analysis], "fundamentals_report")
    
    bull_researcher_node = create_researcher_node(llm_quick, mock_memory, bull_prompt, "Bull Researcher")
    bear_researcher_node = create_researcher_node(llm_quick, mock_memory, bear_prompt, "Bear Researcher")
    research_manager_node = create_research_manager(llm_deep, mock_memory)
    
    trader_node_func = create_trader(llm_quick, mock_memory)
    trader_node = lambda state: trader_node_func(state, "Trader")
    
    risky_node = create_risk_debator(llm_quick, risky_prompt, "Risky Analyst")
    safe_node = create_risk_debator(llm_quick, safe_prompt, "Safe Analyst")
    neutral_node = create_risk_debator(llm_quick, neutral_prompt, "Neutral Analyst")
    risk_manager_node = create_risk_manager(llm_deep, mock_memory)
    
    # Create the workflow
    workflow = StateGraph(AgentState)
    
    # Add Analyst Nodes
    workflow.add_node("Market Analyst", market_analyst_node)
    workflow.add_node("Social Analyst", social_analyst_node)
    workflow.add_node("News Analyst", news_analyst_node)
    workflow.add_node("Fundamentals Analyst", fundamentals_analyst_node)
    workflow.add_node("tools", tool_node)
    workflow.add_node("Msg Clear", msg_clear_node)
    
    # Add Researcher Nodes
    workflow.add_node("Bull Researcher", bull_researcher_node)
    workflow.add_node("Bear Researcher", bear_researcher_node)
    workflow.add_node("Research Manager", research_manager_node)
    
    # Add Trader and Risk Nodes
    workflow.add_node("Trader", trader_node)
    workflow.add_node("Risky Analyst", risky_node)
    workflow.add_node("Safe Analyst", safe_node)
    workflow.add_node("Neutral Analyst", neutral_node)
    workflow.add_node("Risk Judge", risk_manager_node)
    
    # Define Entry Point and Edges - Simplified sequential flow
    workflow.set_entry_point("Market Analyst")
    
    # Sequential analyst flow (no ReAct loops for now)
    workflow.add_edge("Market Analyst", "Social Analyst")
    workflow.add_edge("Social Analyst", "News Analyst")
    workflow.add_edge("News Analyst", "Fundamentals Analyst")
    workflow.add_edge("Fundamentals Analyst", "Bull Researcher")

    # Research debate loop
    workflow.add_conditional_edges("Bull Researcher", conditional_logic.should_continue_debate)
    workflow.add_conditional_edges("Bear Researcher", conditional_logic.should_continue_debate)
    workflow.add_edge("Research Manager", "Trader")

    # Risk debate loop
    workflow.add_edge("Trader", "Risky Analyst")
    workflow.add_conditional_edges("Risky Analyst", conditional_logic.should_continue_risk_analysis)
    workflow.add_conditional_edges("Safe Analyst", conditional_logic.should_continue_risk_analysis)
    workflow.add_conditional_edges("Neutral Analyst", conditional_logic.should_continue_risk_analysis)

    workflow.add_edge("Risk Judge", END)
    
    return workflow.compile()

print("StateGraph build function defined successfully.")
