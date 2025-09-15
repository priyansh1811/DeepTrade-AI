# === Extracted from section: 2.1. Code Dependency: Defining the Analyst Agent Logic ===
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.tracing import get_tracer, get_reasoning_tracer, trace_function

def create_analyst_node(llm, toolkit, system_message, tools, output_field):
    # This function creates a LangGraph node for a specific type of analyst.
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         f"You are a helpful AI assistant. {system_message}" \
         " For your reference, the current date is {current_date}. The company we want to look at is {ticker}." \
         " Provide a comprehensive analysis report based on your knowledge."),
        MessagesPlaceholder(variable_name="messages"),
    ])
    chain = prompt | llm

    def analyst_node(state):
        # The node function itself, which will be called by LangGraph.
        tracer = get_tracer()
        reasoning_tracer = get_reasoning_tracer()
        
        # Extract agent name from system message
        agent_name = system_message.split("You are a ")[1].split(".")[0].title() + " Analyst"
        
        # Start tracing
        from src.tracing.execution_trace import TraceLevel
        tracer.add_step(
            agent_name=agent_name,
            message=f"🚀 Starting {agent_name} analysis",
            level=TraceLevel.INFO
        )
        
        # Start reasoning trace
        reasoning_step_id = reasoning_tracer.start_reasoning(
            agent_name=agent_name,
            initial_thought=f"Analyzing {state['company_of_interest']} for {state['trade_date']}. My role is to {system_message.lower()}"
        )
        
        try:
            # Add evidence about the analysis context
            reasoning_tracer.add_evidence(
                reasoning_step_id,
                f"Stock: {state['company_of_interest']}, Date: {state['trade_date']}",
                "Input Parameters"
            )
            
            # Invoke the LLM
            tracer.add_step(
                agent_name=agent_name,
                message="🤖 Invoking LLM for analysis",
                level=TraceLevel.INFO
            )
            
            result = chain.invoke({
                "messages": state["messages"],
                "current_date": state["trade_date"],
                "ticker": state["company_of_interest"]
            })
            
            # Add reasoning about the result
            reasoning_tracer.continue_reasoning(
                reasoning_step_id,
                f"Generated analysis report with {len(result.content)} characters. The analysis covers key aspects of {state['company_of_interest']}.",
                confidence=0.8
            )
            
            # Conclude reasoning
            reasoning_tracer.conclude_reasoning(
                reasoning_step_id,
                f"Successfully completed {agent_name} analysis",
                confidence=0.85,
                next_action="Pass results to next agent"
            )
            
            # Add success trace
            tracer.add_success(
                agent_name=agent_name,
                message=f"✅ Completed {agent_name} analysis",
                data={"report_length": len(result.content), "output_field": output_field}
            )
            
            report = result.content
            return {"messages": [result], output_field: report}
            
        except Exception as e:
            # Add error trace
            tracer.add_error(
                agent_name=agent_name,
                error=f"Failed {agent_name} analysis: {str(e)}"
            )
            
            # Conclude reasoning with error
            reasoning_tracer.conclude_reasoning(
                reasoning_step_id,
                f"Analysis failed: {str(e)}",
                confidence=0.0,
                next_action="Handle error and continue"
            )
            
            raise
    return analyst_node

# System messages for different analyst types
market_analyst_system_message = "You are a trading assistant specialized in analyzing financial markets. Your role is to select the most relevant technical indicators to analyze a stock's price action, momentum, and volatility. You must use your tools to get historical data and then generate a report with your findings, including a summary table."

social_analyst_system_message = "You are a social media analyst. Your job is to analyze social media posts and public sentiment for a specific company over the past week. Use your tools to find relevant discussions and write a comprehensive report detailing your analysis, insights, and implications for traders, including a summary table."

news_analyst_system_message = "You are a news researcher analyzing recent news and trends over the past week. Write a comprehensive report on the current state of the world relevant for trading and macroeconomics. Use your tools to be comprehensive and provide detailed analysis, including a summary table."

fundamentals_analyst_system_message = "You are a researcher analyzing fundamental information about a company. Write a comprehensive report on the company's financials, insider sentiment, and transactions to gain a full view of its fundamental health, including a summary table."

print("Analyst agent creation functions are now available.")
