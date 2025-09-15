import argparse

def get_inputs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ticker', default='AAPL')
    parser.add_argument('--date', dest='trade_date', default='2025-09-10')
    args = parser.parse_args()
    return args.ticker, args.trade_date