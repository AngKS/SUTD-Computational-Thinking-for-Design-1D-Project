import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-5-nano"  # Using more cost-effective model
MAX_TOKENS = 8500  # Reduced max tokens for efficiency
TEMPERATURE = 0.3  # Lower for more deterministic responses
