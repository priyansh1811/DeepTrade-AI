from src.cli_inputs import get_inputs  # optional helper if defined
from src.graph.build import build_graph
from src.run_pipeline import run_full_pipeline  # optional helper if defined
from src.eval.signal import extract_signal

def main():
    try:
        ticker, trade_date = get_inputs()
    except Exception:
        # fallback
        ticker, trade_date = "AAPL", "2025-09-10"
    graph = build_graph()
    final_state = run_full_pipeline(graph, ticker, trade_date)
    signal = extract_signal(final_state)
    print("Final Signal:", signal)

if __name__ == "__main__":
    main()