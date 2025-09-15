# 🚀 Deep Thinking Trading System - Setup Guide

## ✅ Current Status
Your trading system is **fully functional** and ready to use! All errors have been fixed and the system is working correctly.

## 🔑 API Key Setup

### Option 1: Use the Setup Script (Recommended)
```bash
python setup_api_keys.py
```
This interactive script will help you configure all your API keys.

### Option 2: Manual Setup
Edit the `.env` file and replace the placeholder values:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Finnhub API Configuration (for market data)
FINNHUB_API_KEY=your-actual-finnhub-key-here

# Tavily API Configuration (for web search)
TAVILY_API_KEY=your-actual-tavily-key-here
```

## 🎯 How to Run the System

### Basic Usage
```bash
python main.py --ticker AAPL --date 2025-09-10
```

### Available Options
- `--ticker`: Stock symbol (e.g., AAPL, MSFT, GOOGL)
- `--date`: Trading date in YYYY-MM-DD format

### Examples
```bash
# Analyze Apple stock for a specific date
python main.py --ticker AAPL --date 2025-09-10

# Analyze Microsoft stock
python main.py --ticker MSFT --date 2025-09-15

# Analyze Google stock
python main.py --ticker GOOGL --date 2025-09-20
```

## 🏗️ System Architecture

The system uses a multi-agent approach with the following components:

### 1. **Analyst Agents**
- **Market Analyst**: Technical indicators and price action
- **Social Analyst**: Social media sentiment analysis
- **News Analyst**: Company and macroeconomic news
- **Fundamentals Analyst**: Financial health and metrics

### 2. **Research Team**
- **Bull Researcher**: Argues for buying the stock
- **Bear Researcher**: Argues against buying the stock
- **Research Manager**: Makes final investment recommendation

### 3. **Trading & Risk Team**
- **Trader**: Creates trading proposal
- **Risk Analysts**: Evaluate risk from different perspectives
- **Risk Manager**: Makes final trading decision

## 🔧 Current Features

### ✅ Working Features
- ✅ Complete multi-agent trading analysis pipeline
- ✅ Real-time market data from Yahoo Finance
- ✅ Technical indicators calculation
- ✅ Mock data fallbacks when API keys not configured
- ✅ Command-line interface
- ✅ Signal extraction (BUY/SELL/HOLD)

### 🔄 API Integration Status
- **OpenAI**: Ready for real LLM integration
- **Finnhub**: Ready for real news data
- **Tavily**: Ready for real web search
- **Yahoo Finance**: Already working (no API key needed)

## 🚨 Troubleshooting

### If you get API key errors:
1. Make sure your `.env` file has the correct API keys
2. Check that the keys don't have extra spaces or quotes
3. Verify the keys are valid and active

### If you get import errors:
1. Make sure all dependencies are installed: `pip install -r requirements.txt`
2. Check that you're in the correct directory

### If the system runs but gives mock responses:
1. This is normal when API keys are not configured
2. Configure your API keys to get real analysis

## 📊 Expected Output

When running successfully, you should see:
```
Using real OpenAI LLMs
Tavily search tool initialized successfully
Final Signal: BUY/SELL/HOLD
```

## 🎉 Next Steps

1. **Set up your API keys** using the setup script
2. **Test with different stocks** to see the analysis
3. **Customize the prompts** in the agent files if needed
4. **Add more data sources** by extending the tools

## 📁 Key Files

- `main.py`: Main entry point
- `src/graph/build.py`: Graph construction and LLM integration
- `src/tools.py`: Data fetching tools
- `src/agents/`: Agent implementations
- `.env`: API key configuration
- `setup_api_keys.py`: Interactive setup script

Your system is ready to go! 🚀


