import os
# from dotenv import load_dotenv
import streamlit as st
# load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]
OPENAI_MODEL = "openai/gpt-oss-20b"  # Using more cost-effective model
MAX_TOKENS = 8500  # Reduced max tokens for efficiency
TEMPERATURE = 0.3  # Lower for more deterministic responses
