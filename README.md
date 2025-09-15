# Deep Thinking Trading System (VS Code Project)

This repository is an extracted VS Code–ready version of your Jupyter notebook **Deep Thinking Trading System**.

## Quick Start

1. **Create a virtual environment** (recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   - Copy `.env.example` to `.env` and fill the keys.

4. **Run**
   ```bash
   python main.py --ticker AAPL --date 2025-09-10
   ```

## Project Structure

- `config/` → configuration dictionary and constants
- `src/llms.py` → model initialization (deep & quick thinking)
- `src/state.py` → LangGraph state classes (AgentState, etc.)
- `src/tools.py` → live-data tools: yfinance, finnhub, tavily, stockstats
- `src/memory.py` → FinancialSituationMemory (ChromaDB-based)
- `src/agents/` → analyst, research, trader & risk agents
- `src/graph/` → helpers, nodes, and graph assembly
- `src/eval/` → reflection, signal extraction, judge, backtest, audit, usage
- `main.py` → CLI entrypoint