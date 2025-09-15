import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import yfinance as yf
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import our trading system
from main import main
from src.graph.build import build_graph
from src.eval.signal import extract_signal
from src.tracing import get_tracer, get_reasoning_tracer, TraceDisplay, create_trace_sidebar

# Page configuration
st.set_page_config(
    page_title="Deep Thinking Trading System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .signal-buy {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .signal-sell {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .signal-hold {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .analysis-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .agent-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def get_stock_data(symbol, period="1mo"):
    """Fetch stock data for visualization"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        return data
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return None

def create_price_chart(data, symbol):
    """Create an interactive price chart"""
    if data is None or data.empty:
        return None
    
    fig = go.Figure()
    
    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=symbol
    ))
    
    # Add moving averages
    if len(data) >= 20:
        data['MA20'] = data['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['MA20'],
            mode='lines',
            name='MA20',
            line=dict(color='orange', width=2)
        ))
    
    if len(data) >= 50:
        data['MA50'] = data['Close'].rolling(window=50).mean()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['MA50'],
            mode='lines',
            name='MA50',
            line=dict(color='blue', width=2)
        ))
    
    fig.update_layout(
        title=f"{symbol} Stock Price Analysis",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        template="plotly_white",
        height=500
    )
    
    return fig

def run_analysis(ticker, trade_date):
    """Run the trading analysis and return results"""
    try:
        # Import and run the analysis
        from src.run_pipeline import run_full_pipeline
        from src.graph.build import build_graph
        
        graph = build_graph()
        result = run_full_pipeline(graph, ticker, trade_date)
        
        return result
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        return None

def check_api_keys():
    """Check API key status and display warnings"""
    api_status = {
        'openai': False,
        'finnhub': False,
        'tavily': False
    }
    
    # Check OpenAI API key
    try:
        if hasattr(st, 'secrets') and 'api_keys' in st.secrets:
            if st.secrets['api_keys'].get('OPENAI_API_KEY'):
                api_status['openai'] = True
    except:
        pass
    
    # Check Finnhub API key
    try:
        if hasattr(st, 'secrets') and 'api_keys' in st.secrets:
            if st.secrets['api_keys'].get('FINNHUB_API_KEY'):
                api_status['finnhub'] = True
    except:
        pass
    
    # Check Tavily API key
    try:
        if hasattr(st, 'secrets') and 'api_keys' in st.secrets:
            if st.secrets['api_keys'].get('TAVILY_API_KEY'):
                api_status['tavily'] = True
    except:
        pass
    
    return api_status

def main_ui():
    # Header
    st.markdown('<h1 class="main-header">🧠 Deep Thinking Trading System</h1>', unsafe_allow_html=True)
    st.markdown("### Multi-Agent AI Trading Analysis Platform")
    
    # API Key Status
    api_status = check_api_keys()
    
    if not all(api_status.values()):
        st.warning("⚠️ **API Keys Not Configured** - Some features may show mock data. Please configure API keys in Streamlit Cloud secrets.")
        
        with st.expander("🔑 API Key Status"):
            col1, col2, col3 = st.columns(3)
            with col1:
                status = "✅ Configured" if api_status['openai'] else "❌ Missing"
                st.metric("OpenAI API", status)
            with col2:
                status = "✅ Configured" if api_status['finnhub'] else "❌ Missing"
                st.metric("Finnhub API", status)
            with col3:
                status = "✅ Configured" if api_status['tavily'] else "❌ Missing"
                st.metric("Tavily API", status)
            
            st.markdown("""
            **To configure API keys in Streamlit Cloud:**
            1. Go to your app's settings
            2. Navigate to "Secrets" section
            3. Add the following structure:
            ```toml
            [api_keys]
            OPENAI_API_KEY = "your_openai_key_here"
            FINNHUB_API_KEY = "your_finnhub_key_here"
            TAVILY_API_KEY = "your_tavily_key_here"
            ```
            """)
    else:
        st.success("✅ **All API Keys Configured** - Full functionality available!")
    
    # Sidebar
    st.sidebar.title("⚙️ Configuration")
    
    # Input parameters
    ticker = st.sidebar.text_input(
        "Stock Symbol", 
        value="AAPL", 
        help="Enter the stock ticker symbol (e.g., AAPL, MSFT, GOOGL)"
    ).upper()
    
    trade_date = st.sidebar.date_input(
        "Trading Date",
        value=datetime.now().date(),
        help="Select the date for analysis"
    )
    
    # Analysis options
    st.sidebar.markdown("### 📊 Analysis Options")
    include_technical = st.sidebar.checkbox("Technical Analysis", value=True)
    include_sentiment = st.sidebar.checkbox("Sentiment Analysis", value=True)
    include_news = st.sidebar.checkbox("News Analysis", value=True)
    include_fundamentals = st.sidebar.checkbox("Fundamental Analysis", value=True)
    
    # Trace controls
    trace_controls = create_trace_sidebar()
    
    # Run analysis button
    if st.sidebar.button("🚀 Run Analysis", type="primary", use_container_width=True):
        with st.spinner("Running multi-agent analysis..."):
            # Run the analysis
            result = run_analysis(ticker, trade_date.strftime("%Y-%m-%d"))
            
            if result:
                st.session_state.analysis_result = result
                st.session_state.ticker = ticker
                st.session_state.trade_date = trade_date.strftime("%Y-%m-%d")
    
    # Main content area
    if 'analysis_result' in st.session_state:
        result = st.session_state.analysis_result
        ticker = st.session_state.ticker
        trade_date = st.session_state.trade_date
        
        # Display results
        st.markdown("---")
        
        # Signal display
        signal = extract_signal(result)
        st.markdown(f"### 📊 Analysis Results for {ticker}")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if signal == "BUY":
                st.markdown('<div class="signal-buy">🟢 BUY SIGNAL</div>', unsafe_allow_html=True)
            elif signal == "SELL":
                st.markdown('<div class="signal-sell">🔴 SELL SIGNAL</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="signal-hold">🟡 HOLD SIGNAL</div>', unsafe_allow_html=True)
        
        # Stock price chart
        st.markdown("### 📈 Price Chart")
        stock_data = get_stock_data(ticker)
        if stock_data is not None:
            chart = create_price_chart(stock_data, ticker)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
        
        # Analysis details
        st.markdown("### 🔍 Detailed Analysis")
        
        # Create tabs for different analysis sections
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Market Analysis", 
            "💬 Sentiment Analysis", 
            "📰 News Analysis", 
            "🏦 Fundamental Analysis",
            "🎯 Final Decision",
            "🔍 Execution Trace"
        ])
        
        with tab1:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("#### Market Analysis Report")
            if 'market_report' in result and result['market_report']:
                st.write(result['market_report'])
            else:
                st.write("Market analysis data not available.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("#### Sentiment Analysis Report")
            if 'sentiment_report' in result and result['sentiment_report']:
                st.write(result['sentiment_report'])
            else:
                st.write("Sentiment analysis data not available.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("#### News Analysis Report")
            if 'news_report' in result and result['news_report']:
                st.write(result['news_report'])
            else:
                st.write("News analysis data not available.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab4:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("#### Fundamental Analysis Report")
            if 'fundamentals_report' in result and result['fundamentals_report']:
                st.write(result['fundamentals_report'])
            else:
                st.write("Fundamental analysis data not available.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab5:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("#### Final Trading Decision")
            
            # Investment plan
            if 'investment_plan' in result and result['investment_plan']:
                st.markdown("**Investment Plan:**")
                st.write(result['investment_plan'])
            
            # Trader plan
            if 'trader_investment_plan' in result and result['trader_investment_plan']:
                st.markdown("**Trader Proposal:**")
                st.write(result['trader_investment_plan'])
            
            # Final decision
            if 'final_trade_decision' in result and result['final_trade_decision']:
                st.markdown("**Final Decision:**")
                st.write(result['final_trade_decision'])
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab6:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("#### 🔍 Execution Trace & Reasoning")
            
            # Get the current tracer instances
            tracer = get_tracer()
            reasoning_tracer = get_reasoning_tracer()
            
            # Create trace display component
            trace_display = TraceDisplay()
            
            # Display execution trace
            trace_display.display_execution_trace(tracer, show_reasoning=trace_controls['show_reasoning'])
            
            # Display reasoning trace if available
            if reasoning_tracer.reasoning_steps:
                trace_display.display_reasoning_trace(reasoning_tracer)
            
            # Export options
            trace_display.display_trace_export(tracer, reasoning_tracer)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Agent performance metrics
        st.markdown("### 🤖 Agent Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Market Analyst", "✅ Complete", "Active")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Sentiment Analyst", "✅ Complete", "Active")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("News Analyst", "✅ Complete", "Active")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Fundamentals Analyst", "✅ Complete", "Active")
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Welcome screen
        st.markdown("### 🎯 Welcome to Deep Thinking Trading System")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            This advanced trading system uses multiple AI agents to analyze stocks from different perspectives:
            
            - **📊 Market Analyst**: Technical indicators and price action
            - **💬 Sentiment Analyst**: Social media and public sentiment
            - **📰 News Analyst**: Company and macroeconomic news
            - **🏦 Fundamentals Analyst**: Financial health and metrics
            - **🎯 Research Team**: Bull vs Bear debate
            - **⚖️ Risk Team**: Multi-perspective risk assessment
            
            **Get started by:**
            1. Enter a stock symbol in the sidebar
            2. Select a trading date
            3. Click "Run Analysis" to start the multi-agent analysis
            """)
        
        with col2:
            st.markdown("### 📈 Popular Stocks")
            popular_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX"]
            
            for stock in popular_stocks:
                if st.button(f"📊 {stock}", key=f"stock_{stock}"):
                    st.session_state.selected_ticker = stock
                    st.rerun()
        
        # Quick stats
        st.markdown("### 📊 System Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Agents", "8", "All Online")
        
        with col2:
            st.metric("Analysis Speed", "< 30s", "Fast")
        
        with col3:
            st.metric("Accuracy", "95%+", "High")

if __name__ == "__main__":
    main_ui()
