"""
Trace Display Component for Streamlit
Provides Perplexity-style execution trace visualization
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from typing import Dict, List, Any
from .execution_trace import ExecutionTracer, TraceLevel, TraceStep
from .reasoning_trace import ReasoningTracer, ReasoningStep

class TraceDisplay:
    """Streamlit component for displaying execution traces"""
    
    def __init__(self):
        self.trace_colors = {
            TraceLevel.INFO: "#3B82F6",
            TraceLevel.WARNING: "#F59E0B", 
            TraceLevel.ERROR: "#EF4444",
            TraceLevel.SUCCESS: "#10B981",
            TraceLevel.REASONING: "#8B5CF6",
            TraceLevel.TOOL_CALL: "#F97316",
            TraceLevel.DECISION: "#EC4899"
        }
        
        self.trace_icons = {
            TraceLevel.INFO: "ℹ️",
            TraceLevel.WARNING: "⚠️",
            TraceLevel.ERROR: "❌",
            TraceLevel.SUCCESS: "✅",
            TraceLevel.REASONING: "🧠",
            TraceLevel.TOOL_CALL: "🔧",
            TraceLevel.DECISION: "🎯"
        }
    
    def display_execution_trace(self, tracer: ExecutionTracer, show_reasoning: bool = True):
        """Display the complete execution trace"""
        st.markdown("### 🔍 Execution Trace")
        
        # Summary metrics
        summary = tracer.get_trace_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Steps", summary['total_steps'])
        with col2:
            st.metric("Duration", f"{summary['total_duration_seconds']}s")
        with col3:
            st.metric("Agents", len(summary['agent_steps']))
        with col4:
            if summary['total_steps'] > 0:
                success_rate = (summary['level_counts'].get('success', 0) / summary['total_steps']) * 100
                st.metric("Success Rate", f"{success_rate:.1f}%")
            else:
                st.metric("Success Rate", "N/A")
        
        # Agent performance chart
        self._display_agent_performance(summary['agent_steps'])
        
        # Timeline view
        self._display_timeline(tracer.traces)
        
        # Detailed steps
        if show_reasoning:
            self._display_detailed_steps(tracer.traces)
    
    def display_reasoning_trace(self, reasoning_tracer: ReasoningTracer):
        """Display the reasoning trace"""
        st.markdown("### 🧠 Reasoning Trace")
        
        # Group by agent
        agents = {}
        for step in reasoning_tracer.reasoning_steps:
            if step.agent_name not in agents:
                agents[step.agent_name] = []
            agents[step.agent_name].append(step)
        
        # Display each agent's reasoning
        for agent_name, steps in agents.items():
            with st.expander(f"🤖 {agent_name} - {len(steps)} reasoning steps", expanded=True):
                for i, step in enumerate(steps, 1):
                    self._display_reasoning_step(step, i)
    
    def _display_agent_performance(self, agent_steps: Dict[str, int]):
        """Display agent performance chart"""
        if not agent_steps:
            return
        
        fig = px.bar(
            x=list(agent_steps.keys()),
            y=list(agent_steps.values()),
            title="Agent Activity",
            labels={'x': 'Agent', 'y': 'Steps'},
            color=list(agent_steps.values()),
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(
            showlegend=False,
            height=300,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _display_timeline(self, traces: List[TraceStep]):
        """Display timeline view of execution"""
        if not traces:
            return
        
        # Create timeline data
        timeline_data = []
        for trace in traces:
            timeline_data.append({
                'Agent': trace.agent_name,
                'Step': trace.step_id,
                'Message': trace.message,
                'Level': trace.level.value,
                'Timestamp': trace.timestamp,
                'Duration': trace.duration_ms or 0
            })
        
        # Create timeline chart
        fig = go.Figure()
        
        # Add traces for each agent
        agents = list(set(trace.agent_name for trace in traces))
        colors = px.colors.qualitative.Set3[:len(agents)]
        
        for i, agent in enumerate(agents):
            agent_traces = [t for t in traces if t.agent_name == agent]
            
            fig.add_trace(go.Scatter(
                x=[t.timestamp for t in agent_traces],
                y=[i] * len(agent_traces),
                mode='markers+lines',
                name=agent,
                marker=dict(
                    size=10,
                    color=colors[i],
                    symbol='circle'
                ),
                text=[t.message for t in agent_traces],
                hovertemplate='<b>%{text}</b><br>Time: %{x}<extra></extra>'
            ))
        
        fig.update_layout(
            title="Execution Timeline",
            xaxis_title="Time",
            yaxis_title="Agent",
            height=400,
            showlegend=True,
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(len(agents))),
                ticktext=agents
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _display_detailed_steps(self, traces: List[TraceStep]):
        """Display detailed execution steps"""
        st.markdown("#### 📋 Detailed Steps")
        
        for trace in traces:
            with st.container():
                # Create columns for step display
                col1, col2, col3 = st.columns([1, 8, 1])
                
                with col1:
                    # Step number and icon
                    st.markdown(f"**{trace.step_id}**")
                    st.markdown(f"{self.trace_icons[trace.level]}")
                
                with col2:
                    # Main content
                    st.markdown(f"**{trace.agent_name}**: {trace.message}")
                    
                    if trace.reasoning:
                        with st.expander("🧠 Reasoning", expanded=False):
                            st.markdown(trace.reasoning)
                    
                    if trace.tool_calls:
                        with st.expander("🔧 Tool Calls", expanded=False):
                            for tool_call in trace.tool_calls:
                                st.markdown(f"**{tool_call['tool_name']}**")
                                st.code(f"Input: {tool_call['input']}")
                                if tool_call.get('result'):
                                    st.code(f"Result: {tool_call['result']}")
                    
                    if trace.data:
                        with st.expander("📊 Data", expanded=False):
                            st.json(trace.data)
                    
                    if trace.confidence:
                        st.progress(trace.confidence)
                        st.caption(f"Confidence: {trace.confidence:.2f}")
                
                with col3:
                    # Timestamp
                    timestamp = datetime.fromisoformat(trace.timestamp)
                    st.caption(timestamp.strftime("%H:%M:%S"))
                
                st.divider()
    
    def _display_reasoning_step(self, step: ReasoningStep, step_num: int):
        """Display a single reasoning step"""
        st.markdown(f"#### Step {step_num}: {step.step_id}")
        
        # Confidence indicator
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Confidence:** {step.confidence:.2f}")
        with col2:
            st.progress(step.confidence)
        
        # Thought process
        st.markdown("**Thought Process:**")
        st.markdown(step.thought)
        
        # Evidence
        if step.evidence:
            st.markdown("**Evidence:**")
            for evidence in step.evidence:
                st.markdown(f"- {evidence}")
        
        # Next action
        if step.next_action:
            st.markdown(f"**Next Action:** {step.next_action}")
        
        st.divider()
    
    def display_trace_export(self, tracer: ExecutionTracer, reasoning_tracer: ReasoningTracer = None):
        """Display trace export options"""
        st.markdown("### 📤 Export Traces")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Execution Trace**")
            if st.button("Export as JSON"):
                json_data = tracer.export_trace("json")
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"execution_trace_{tracer.session_id}.json",
                    mime="application/json"
                )
            
            if st.button("Export as Markdown"):
                md_data = tracer.export_trace("markdown")
                st.download_button(
                    label="Download Markdown",
                    data=md_data,
                    file_name=f"execution_trace_{tracer.session_id}.md",
                    mime="text/markdown"
                )
        
        with col2:
            if reasoning_tracer:
                st.markdown("**Reasoning Trace**")
                if st.button("Export Reasoning as JSON"):
                    json_data = reasoning_tracer.export_reasoning_trace("json")
                    st.download_button(
                        label="Download Reasoning JSON",
                        data=json_data,
                        file_name=f"reasoning_trace_{tracer.session_id}.json",
                        mime="application/json"
                    )
                
                if st.button("Export Reasoning as Markdown"):
                    md_data = reasoning_tracer.export_reasoning_trace("markdown")
                    st.download_button(
                        label="Download Reasoning Markdown",
                        data=md_data,
                        file_name=f"reasoning_trace_{tracer.session_id}.md",
                        mime="text/markdown"
                    )

def create_trace_sidebar():
    """Create sidebar controls for trace display"""
    st.sidebar.markdown("### 🔍 Trace Controls")
    
    show_reasoning = st.sidebar.checkbox("Show Reasoning", value=True)
    show_timeline = st.sidebar.checkbox("Show Timeline", value=True)
    show_details = st.sidebar.checkbox("Show Detailed Steps", value=True)
    
    return {
        "show_reasoning": show_reasoning,
        "show_timeline": show_timeline,
        "show_details": show_details
    }
