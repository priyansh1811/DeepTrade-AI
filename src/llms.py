# === Extracted from section: 1.3. Initializing the Language Models (LLMs) ===
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Get API key from environment or Streamlit secrets
openai_api_key = os.getenv("OPENAI_API_KEY")

# Try to get API key from Streamlit secrets if available
try:
    import streamlit as st
    if hasattr(st, 'secrets') and 'api_keys' in st.secrets:
        openai_api_key = st.secrets['api_keys']['OPENAI_API_KEY']
        print("Using OpenAI API key from Streamlit secrets")
except:
    pass

if not openai_api_key or openai_api_key == "your_openai_api_key_here":
    print("Warning: OPENAI_API_KEY not set or still has placeholder value")
    print("Please update your .env file with your actual OpenAI API key")
    # Create mock LLMs for now
    deep_thinking_llm = None
    quick_thinking_llm = None
else:
    # Initialize real LLMs
    deep_thinking_llm = ChatOpenAI(
        model="gpt-4o",
        api_key=openai_api_key,
        temperature=0.1
    )

    quick_thinking_llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=openai_api_key,
        temperature=0.1
    )

    print("LLMs initialized successfully.")
    print(f"Deep Thinking LLM: {deep_thinking_llm}")
    print(f"Quick Thinking LLM: {quick_thinking_llm}")
