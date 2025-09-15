"""
Execution Trace System for Deep Thinking Trading System
Provides Perplexity-style step-by-step reasoning traces
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class TraceLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    REASONING = "reasoning"
    TOOL_CALL = "tool_call"
    DECISION = "decision"

@dataclass
class TraceStep:
    """Individual step in the execution trace"""
    step_id: str
    agent_name: str
    timestamp: str
    level: TraceLevel
    message: str
    reasoning: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = None

class ExecutionTracer:
    """Main execution tracer for the trading system"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"session_{int(time.time())}"
        self.traces: List[TraceStep] = []
        self.current_step = 0
        self.start_time = time.time()
        
    def add_step(self, 
                 agent_name: str, 
                 message: str, 
                 level: TraceLevel = TraceLevel.INFO,
                 reasoning: str = None,
                 data: Dict[str, Any] = None,
                 tool_calls: List[Dict[str, Any]] = None,
                 confidence: float = None) -> str:
        """Add a new step to the execution trace"""
        self.current_step += 1
        step_id = f"step_{self.current_step:03d}"
        
        step = TraceStep(
            step_id=step_id,
            agent_name=agent_name,
            timestamp=datetime.now().isoformat(),
            level=level,
            message=message,
            reasoning=reasoning,
            data=data,
            tool_calls=tool_calls,
            confidence=confidence
        )
        
        self.traces.append(step)
        return step_id
    
    def add_reasoning(self, agent_name: str, reasoning: str, confidence: float = None):
        """Add a reasoning step"""
        return self.add_step(
            agent_name=agent_name,
            message="🧠 Reasoning Process",
            level=TraceLevel.REASONING,
            reasoning=reasoning,
            confidence=confidence
        )
    
    def add_tool_call(self, agent_name: str, tool_name: str, tool_input: Dict[str, Any], result: Any = None):
        """Add a tool call step"""
        tool_calls = [{
            "tool_name": tool_name,
            "input": tool_input,
            "result": str(result) if result else "Executing...",
            "timestamp": datetime.now().isoformat()
        }]
        
        return self.add_step(
            agent_name=agent_name,
            message=f"🔧 Tool Call: {tool_name}",
            level=TraceLevel.TOOL_CALL,
            tool_calls=tool_calls
        )
    
    def add_decision(self, agent_name: str, decision: str, reasoning: str, confidence: float = None):
        """Add a decision step"""
        return self.add_step(
            agent_name=agent_name,
            message=f"🎯 Decision: {decision}",
            level=TraceLevel.DECISION,
            reasoning=reasoning,
            confidence=confidence
        )
    
    def add_success(self, agent_name: str, message: str, data: Dict[str, Any] = None):
        """Add a success step"""
        return self.add_step(
            agent_name=agent_name,
            message=f"✅ {message}",
            level=TraceLevel.SUCCESS,
            data=data
        )
    
    def add_error(self, agent_name: str, error: str, data: Dict[str, Any] = None):
        """Add an error step"""
        return self.add_step(
            agent_name=agent_name,
            message=f"❌ Error: {error}",
            level=TraceLevel.ERROR,
            data=data
        )
    
    def get_trace_summary(self) -> Dict[str, Any]:
        """Get a summary of the execution trace"""
        total_duration = time.time() - self.start_time
        
        # Count steps by level
        level_counts = {}
        for trace in self.traces:
            level_counts[trace.level.value] = level_counts.get(trace.level.value, 0) + 1
        
        # Get agent performance
        agent_steps = {}
        for trace in self.traces:
            agent_steps[trace.agent_name] = agent_steps.get(trace.agent_name, 0) + 1
        
        return {
            "session_id": self.session_id,
            "total_steps": len(self.traces),
            "total_duration_seconds": round(total_duration, 2),
            "level_counts": level_counts,
            "agent_steps": agent_steps,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.now().isoformat()
        }
    
    def get_traces_for_agent(self, agent_name: str) -> List[TraceStep]:
        """Get all traces for a specific agent"""
        return [trace for trace in self.traces if trace.agent_name == agent_name]
    
    def get_reasoning_traces(self) -> List[TraceStep]:
        """Get all reasoning traces"""
        return [trace for trace in self.traces if trace.level == TraceLevel.REASONING]
    
    def get_decision_traces(self) -> List[TraceStep]:
        """Get all decision traces"""
        return [trace for trace in self.traces if trace.level == TraceLevel.DECISION]
    
    def export_trace(self, format: str = "json") -> str:
        """Export the trace in various formats"""
        if format == "json":
            return json.dumps({
                "session_info": self.get_trace_summary(),
                "traces": [asdict(trace) for trace in self.traces]
            }, indent=2)
        elif format == "markdown":
            return self._export_markdown()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_markdown(self) -> str:
        """Export trace as markdown"""
        md = f"# Execution Trace - Session {self.session_id}\n\n"
        
        # Summary
        summary = self.get_trace_summary()
        md += f"**Total Steps:** {summary['total_steps']}\n"
        md += f"**Duration:** {summary['total_duration_seconds']}s\n"
        md += f"**Start Time:** {summary['start_time']}\n\n"
        
        # Agent performance
        md += "## Agent Performance\n\n"
        for agent, count in summary['agent_steps'].items():
            md += f"- **{agent}:** {count} steps\n"
        md += "\n"
        
        # Detailed traces
        md += "## Execution Steps\n\n"
        for trace in self.traces:
            level_emoji = {
                TraceLevel.INFO: "ℹ️",
                TraceLevel.WARNING: "⚠️",
                TraceLevel.ERROR: "❌",
                TraceLevel.SUCCESS: "✅",
                TraceLevel.REASONING: "🧠",
                TraceLevel.TOOL_CALL: "🔧",
                TraceLevel.DECISION: "🎯"
            }
            
            md += f"### {level_emoji[trace.level]} {trace.agent_name} - {trace.message}\n"
            md += f"**Time:** {trace.timestamp}\n"
            
            if trace.reasoning:
                md += f"**Reasoning:** {trace.reasoning}\n"
            
            if trace.confidence:
                md += f"**Confidence:** {trace.confidence:.2f}\n"
            
            if trace.tool_calls:
                md += "**Tool Calls:**\n"
                for tool_call in trace.tool_calls:
                    md += f"- {tool_call['tool_name']}: {tool_call['input']}\n"
            
            if trace.data:
                md += f"**Data:** {json.dumps(trace.data, indent=2)}\n"
            
            md += "\n"
        
        return md

# Global tracer instance
_global_tracer: Optional[ExecutionTracer] = None

def get_tracer() -> ExecutionTracer:
    """Get the global tracer instance"""
    global _global_tracer
    if _global_tracer is None:
        _global_tracer = ExecutionTracer()
    return _global_tracer

def reset_tracer(session_id: str = None):
    """Reset the global tracer"""
    global _global_tracer
    _global_tracer = ExecutionTracer(session_id)

def trace_function(agent_name: str, function_name: str = None):
    """Decorator to trace function execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            func_name = function_name or func.__name__
            
            tracer.add_step(
                agent_name=agent_name,
                message=f"🚀 Starting {func_name}",
                level=TraceLevel.INFO
            )
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                
                tracer.add_success(
                    agent_name=agent_name,
                    message=f"✅ Completed {func_name}",
                    data={"result": str(result)[:200] + "..." if len(str(result)) > 200 else str(result)},
                    confidence=1.0
                )
                
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                tracer.add_error(
                    agent_name=agent_name,
                    message=f"❌ Failed {func_name}",
                    data={"error": str(e)}
                )
                raise
        return wrapper
    return decorator


