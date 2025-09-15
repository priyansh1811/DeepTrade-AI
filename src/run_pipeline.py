def run_full_pipeline(graph, ticker, trade_date):
    """Run the complete trading analysis pipeline."""
    from src.state import AgentState, InvestDebateState, RiskDebateState
    from langchain_core.messages import HumanMessage
    from src.tracing import reset_tracer, reset_reasoning_tracer, get_tracer, get_reasoning_tracer
    
    # Initialize the complete state
    initial_state = {
        'messages': [HumanMessage(content=f"Analyze {ticker} stock for trading on {trade_date}")],
        'company_of_interest': ticker,
        'trade_date': trade_date,
        'sender': 'User',
        'market_report': '',
        'sentiment_report': '',
        'news_report': '',
        'fundamentals_report': '',
        'investment_debate_state': {
            'bull_history': '',
            'bear_history': '',
            'history': '',
            'current_response': '',
            'judge_decision': '',
            'count': 0
        },
        'investment_plan': '',
        'trader_investment_plan': '',
        'risk_debate_state': {
            'risky_history': '',
            'safe_history': '',
            'neutral_history': '',
            'history': '',
            'latest_speaker': '',
            'current_risky_response': '',
            'current_safe_response': '',
            'current_neutral_response': '',
            'judge_decision': '',
            'count': 0
        },
        'final_trade_decision': ''
    }
    
    try:
        print(f"🚀 Starting analysis for {ticker} on {trade_date}")
        print("📊 Running multi-agent trading analysis pipeline...")
        
        # Reset tracers for new analysis
        reset_tracer(f"analysis_{ticker}_{trade_date}")
        reset_reasoning_tracer()
        
        # Get tracers
        tracer = get_tracer()
        reasoning_tracer = get_reasoning_tracer()
        
        # Add initial trace
        from src.tracing.execution_trace import TraceLevel
        tracer.add_step(
            agent_name="System",
            message="🚀 Starting Deep Thinking Trading Analysis",
            level=TraceLevel.INFO,
            data={"ticker": ticker, "trade_date": trade_date}
        )
        
        # Run the graph with proper state
        result = graph.invoke(initial_state)
        
        # Add completion trace
        tracer.add_success(
            agent_name="System",
            message="✅ Analysis completed successfully",
            data={"final_signal": result.get('final_trade_decision', 'Unknown')}
        )
        
        print("✅ Analysis completed successfully!")
        return result
        
    except Exception as e:
        print(f"❌ Error in pipeline: {e}")
        return {
            'final_trade_decision': 'HOLD - Analysis failed',
            'error': str(e),
            'company_of_interest': ticker,
            'trade_date': trade_date
        }