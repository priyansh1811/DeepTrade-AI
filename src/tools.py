# === Extracted from section: 1.5. Code Dependency: Defining the Live Data Tools and `Toolkit` ===
import os
import yfinance as yf
import finnhub
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Annotated
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from stockstats import wrap as stockstats_wrap
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Tool Implementations ---

@tool
def get_yfinance_data(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """Retrieve the stock price data for a given ticker symbol from Yahoo Finance."""
    try:
        ticker = yf.Ticker(symbol.upper())
        data = ticker.history(start=start_date, end=end_date)
        if data.empty:
            return f"No data found for symbol '{symbol}' between {start_date} and {end_date}"
        return data.to_csv()
    except Exception as e:
        return f"Error fetching Yahoo Finance data: {e}"

@tool
def get_technical_indicators(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """Retrieve key technical indicators for a stock using stockstats library."""
    try:
        df = yf.download(symbol, start=start_date, end=end_date, progress=False)
        if df.empty:
            return "No data to calculate indicators."
        stock_df = stockstats_wrap(df)
        indicators = stock_df[['macd', 'rsi_14', 'boll', 'boll_ub', 'boll_lb', 'close_50_sma', 'close_200_sma']]
        return indicators.tail().to_csv() # Return last 5 days for brevity
    except Exception as e:
        return f"Error calculating stockstats indicators: {e}"

@tool
def get_finnhub_news(ticker: str, start_date: str, end_date: str) -> str:
    """Get company news from Finnhub within a date range."""
    finnhub_api_key = os.getenv("FINNHUB_API_KEY")
    
    # Try to get API key from Streamlit secrets if available
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'api_keys' in st.secrets:
            finnhub_api_key = st.secrets['api_keys']['FINNHUB_API_KEY']
    except:
        pass
    
    if not finnhub_api_key or finnhub_api_key == "your_finnhub_api_key_here":
        return f"Finnhub API key not configured. Mock news for {ticker} on {start_date}: Strong earnings report and positive market sentiment."
    
    try:
        finnhub_client = finnhub.Client(api_key=finnhub_api_key)
        news_list = finnhub_client.company_news(ticker, _from=start_date, to=end_date)
        news_items = []
        for news in news_list[:5]: # Limit to 5 results
            news_items.append(f"Headline: {news['headline']}\nSummary: {news['summary']}")
        return "\n\n".join(news_items) if news_items else "No Finnhub news found."
    except Exception as e:
        return f"Error fetching Finnhub news: {e}"

# The following three tools use Tavily for live, real-time web search.
# Initialize Tavily tool only if API key is available
tavily_api_key = os.getenv("TAVILY_API_KEY")

# Try to get API key from Streamlit secrets if available
try:
    import streamlit as st
    if hasattr(st, 'secrets') and 'api_keys' in st.secrets:
        tavily_api_key = st.secrets['api_keys']['TAVILY_API_KEY']
        print("Using Tavily API key from Streamlit secrets")
except:
    pass

if tavily_api_key and tavily_api_key != "your_tavily_api_key_here":
    try:
        tavily_tool = TavilySearchResults(max_results=3, api_key=tavily_api_key)
        print("Tavily search tool initialized successfully")
    except Exception as e:
        print(f"Warning: Tavily tool not available: {e}")
        tavily_tool = None
else:
    print("Warning: TAVILY_API_KEY not set or still has placeholder value")
    tavily_tool = None

@tool
def get_social_media_sentiment(ticker: str, trade_date: str) -> str:
    """Performs a live web search for social media sentiment regarding a stock."""
    if tavily_tool is None:
        return f"Tavily search not available. Mock sentiment data for {ticker} on {trade_date}: Positive sentiment detected in social media discussions."
    query = f"social media sentiment and discussions for {ticker} stock around {trade_date}"
    return tavily_tool.invoke({"query": query})

@tool
def get_fundamental_analysis(ticker: str, trade_date: str) -> str:
    """Performs a live web search for recent fundamental analysis of a stock."""
    if tavily_tool is None:
        return f"Tavily search not available. Mock fundamental analysis for {ticker} on {trade_date}: Strong financial metrics and growth potential identified."
    query = f"fundamental analysis and key financial metrics for {ticker} stock published around {trade_date}"
    return tavily_tool.invoke({"query": query})

@tool
def get_macroeconomic_news(trade_date: str) -> str:
    """Performs a live web search for macroeconomic news relevant to the stock market."""
    if tavily_tool is None:
        return f"Tavily search not available. Mock macroeconomic news for {trade_date}: Market conditions stable with moderate volatility expected."
    query = f"macroeconomic news and market trends affecting the stock market on {trade_date}"
    return tavily_tool.invoke({"query": query})

# --- Toolkit Class ---
class Toolkit:
    def __init__(self, config):
        self.config = config
        self.get_yfinance_data = get_yfinance_data
        self.get_technical_indicators = get_technical_indicators
        self.get_finnhub_news = get_finnhub_news
        self.get_social_media_sentiment = get_social_media_sentiment
        self.get_fundamental_analysis = get_fundamental_analysis
        self.get_macroeconomic_news = get_macroeconomic_news

# Note: config will be imported from the calling module
# toolkit = Toolkit(config)
print(f"Toolkit class defined and instantiated with live data tools.")
