import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-5-mini"  # Using more cost-effective model
MAX_TOKENS = 2000
TEMPERATURE = 0.3  # Lower for more deterministic responses
