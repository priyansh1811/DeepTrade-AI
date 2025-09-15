"""
Reasoning Trace System for Deep Thinking Trading System
Captures the step-by-step reasoning process of each AI agent
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from .execution_trace import ExecutionTracer, TraceLevel, get_tracer

@dataclass
class ReasoningStep:
    """Individual reasoning step"""
    step_id: str
    agent_name: str
    timestamp: str
    thought: str
    evidence: List[str]
    confidence: float
    next_action: str
    reasoning_chain: List[str]

class ReasoningTracer:
    """Tracks the reasoning process of AI agents"""
    
    def __init__(self, execution_tracer: ExecutionTracer = None):
        self.execution_tracer = execution_tracer or get_tracer()
        self.reasoning_steps: List[ReasoningStep] = []
        self.current_chain: List[str] = []
    
    def start_reasoning(self, agent_name: str, initial_thought: str) -> str:
        """Start a new reasoning process"""
        step_id = f"reasoning_{len(self.reasoning_steps) + 1:03d}"
        
        step = ReasoningStep(
            step_id=step_id,
            agent_name=agent_name,
            timestamp=datetime.now().isoformat(),
            thought=initial_thought,
            evidence=[],
            confidence=0.0,
            next_action="",
            reasoning_chain=[]
        )
        
        self.reasoning_steps.append(step)
        self.current_chain = [initial_thought]
        
        # Add to execution trace
        self.execution_tracer.add_reasoning(
            agent_name=agent_name,
            reasoning=initial_thought
        )
        
        return step_id
    
    def add_evidence(self, step_id: str, evidence: str, source: str = None):
        """Add evidence to a reasoning step"""
        step = self._get_step(step_id)
        if step:
            evidence_text = f"{evidence} (Source: {source})" if source else evidence
            step.evidence.append(evidence_text)
            
            # Update execution trace
            self.execution_tracer.add_step(
                agent_name=step.agent_name,
                message=f"📊 Evidence: {evidence}",
                level=TraceLevel.INFO,
                data={"source": source}
            )
    
    def continue_reasoning(self, step_id: str, thought: str, confidence: float = None):
        """Continue the reasoning process"""
        step = self._get_step(step_id)
        if step:
            step.thought += f"\n\nNext thought: {thought}"
            if confidence is not None:
                step.confidence = confidence
            
            self.current_chain.append(thought)
            step.reasoning_chain = self.current_chain.copy()
            
            # Update execution trace
            self.execution_tracer.add_reasoning(
                agent_name=step.agent_name,
                reasoning=thought,
                confidence=confidence
            )
    
    def conclude_reasoning(self, step_id: str, conclusion: str, confidence: float, next_action: str):
        """Conclude the reasoning process"""
        step = self._get_step(step_id)
        if step:
            step.thought += f"\n\nConclusion: {conclusion}"
            step.confidence = confidence
            step.next_action = next_action
            
            # Add to execution trace
            self.execution_tracer.add_decision(
                agent_name=step.agent_name,
                decision=conclusion,
                reasoning=step.thought,
                confidence=confidence
            )
    
    def _get_step(self, step_id: str) -> Optional[ReasoningStep]:
        """Get a reasoning step by ID"""
        for step in self.reasoning_steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_reasoning_chain(self, agent_name: str) -> List[ReasoningStep]:
        """Get the complete reasoning chain for an agent"""
        return [step for step in self.reasoning_steps if step.agent_name == agent_name]
    
    def get_evidence_summary(self, agent_name: str) -> Dict[str, List[str]]:
        """Get a summary of all evidence used by an agent"""
        evidence_summary = {}
        for step in self.reasoning_steps:
            if step.agent_name == agent_name:
                evidence_summary[step.step_id] = step.evidence
        return evidence_summary
    
    def export_reasoning_trace(self, format: str = "json") -> str:
        """Export the reasoning trace"""
        if format == "json":
            return json.dumps({
                "reasoning_steps": [asdict(step) for step in self.reasoning_steps],
                "summary": {
                    "total_steps": len(self.reasoning_steps),
                    "agents": list(set(step.agent_name for step in self.reasoning_steps)),
                    "average_confidence": sum(step.confidence for step in self.reasoning_steps) / len(self.reasoning_steps) if self.reasoning_steps else 0
                }
            }, indent=2)
        elif format == "markdown":
            return self._export_markdown()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_markdown(self) -> str:
        """Export reasoning trace as markdown"""
        md = "# Reasoning Trace\n\n"
        
        # Group by agent
        agents = {}
        for step in self.reasoning_steps:
            if step.agent_name not in agents:
                agents[step.agent_name] = []
            agents[step.agent_name].append(step)
        
        for agent_name, steps in agents.items():
            md += f"## {agent_name} Reasoning Process\n\n"
            
            for i, step in enumerate(steps, 1):
                md += f"### Step {i}: {step.step_id}\n"
                md += f"**Time:** {step.timestamp}\n"
                md += f"**Confidence:** {step.confidence:.2f}\n\n"
                
                md += "**Thought Process:**\n"
                md += f"{step.thought}\n\n"
                
                if step.evidence:
                    md += "**Evidence:**\n"
                    for evidence in step.evidence:
                        md += f"- {evidence}\n"
                    md += "\n"
                
                if step.next_action:
                    md += f"**Next Action:** {step.next_action}\n\n"
                
                md += "---\n\n"
        
        return md

# Global reasoning tracer
_global_reasoning_tracer: Optional[ReasoningTracer] = None

def get_reasoning_tracer() -> ReasoningTracer:
    """Get the global reasoning tracer"""
    global _global_reasoning_tracer
    if _global_reasoning_tracer is None:
        _global_reasoning_tracer = ReasoningTracer()
    return _global_reasoning_tracer

def reset_reasoning_tracer():
    """Reset the global reasoning tracer"""
    global _global_reasoning_tracer
    _global_reasoning_tracer = ReasoningTracer()

def trace_reasoning(agent_name: str):
    """Decorator to trace reasoning process"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            reasoning_tracer = get_reasoning_tracer()
            
            # Start reasoning
            step_id = reasoning_tracer.start_reasoning(
                agent_name=agent_name,
                initial_thought=f"Starting {func.__name__} analysis"
            )
            
            try:
                result = func(*args, **kwargs)
                
                # Conclude reasoning
                reasoning_tracer.conclude_reasoning(
                    step_id=step_id,
                    conclusion=f"Completed {func.__name__} successfully",
                    confidence=0.8,
                    next_action="Proceed to next step"
                )
                
                return result
            except Exception as e:
                reasoning_tracer.conclude_reasoning(
                    step_id=step_id,
                    conclusion=f"Failed {func.__name__}: {str(e)}",
                    confidence=0.0,
                    next_action="Handle error"
                )
                raise
        return wrapper
    return decorator


