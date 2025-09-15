# === Extracted from section: 1.2. The Configuration Dictionary: The Control Panel for Our Agents ===
import os
from pprint import pprint

# Define our central configuration for this notebook run
config = {
    "results_dir": "./results",
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o",       # Powerful model for complex reasoning
    "quick_think_llm": "gpt-4o-mini", # Fast, cheaper model for data processing
    "backend_url": "https://api.openai.com/v1",
    # Debate and discussion settings
    "max_debate_rounds": 2, # Bull vs. Bear will have 2 rounds of debate
    "max_risk_discuss_rounds": 1, # Risk team has 1 round of debate
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": True, # Use live APIs instead of cached data
    "data_cache_dir": "./data_cache" # Directory for caching online data
}

# Create the cache directory if it doesn't exist
os.makedirs(config["data_cache_dir"], exist_ok=True)

print("Configuration dictionary created:")
pprint(config)
