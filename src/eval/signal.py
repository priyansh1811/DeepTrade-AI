# === Extracted from section: 7.2. Extracting a Clean BUY, SELL, or HOLD Signal ===

class SignalProcessor:
    def __init__(self, llm):
        self.llm = llm
    
    def process_signal(self, trade_decision):
        """Extract a clean BUY, SELL, or HOLD signal from the trade decision."""
        if not trade_decision:
            return "HOLD"
        
        decision_lower = trade_decision.lower()
        if "buy" in decision_lower:
            return "BUY"
        elif "sell" in decision_lower:
            return "SELL"
        else:
            return "HOLD"

def extract_signal(final_state):
    """Extract the final trading signal from the state."""
    if not final_state or 'final_trade_decision' not in final_state:
        return "HOLD"
    
    processor = SignalProcessor(None)  # Mock LLM for now
    return processor.process_signal(final_state['final_trade_decision'])
