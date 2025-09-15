# === Extracted from section: 5.2. Creating the Tool Nodes for Execution ===
from langgraph.prebuilt import ToolNode
from src.tools import get_yfinance_data, get_technical_indicators, get_finnhub_news, get_social_media_sentiment, get_fundamental_analysis, get_macroeconomic_news
from src.agents.analyst import create_analyst_node
from src.agents.research import create_researcher_node, create_research_manager
from src.agents.trader_risk import create_trader, create_risk_debator, create_risk_manager

all_tools = [
    get_yfinance_data,
    get_technical_indicators,
    get_finnhub_news,
    get_social_media_sentiment,
    get_fundamental_analysis,
    get_macroeconomic_news
]
tool_node = ToolNode(all_tools)

# Create analyst nodes (placeholder implementations - will be properly initialized in build_graph)
market_analyst_node = None
social_analyst_node = None
news_analyst_node = None
fundamentals_analyst_node = None

# Create researcher nodes (placeholder implementations - will be properly initialized in build_graph)
bull_researcher_node = None
bear_researcher_node = None
research_manager_node = None

# Create trader and risk nodes (placeholder implementations - will be properly initialized in build_graph)
trader_node = None
risky_node = None
safe_node = None
neutral_node = None
risk_manager_node = None

print("All node functions created successfully.")
