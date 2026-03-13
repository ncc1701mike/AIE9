import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (works regardless of where script is called from)
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GUARDRAILS_API_KEY = os.getenv("GUARDRAILS_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Validate on import — raises clearly if a key is missing
_required = {
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "GUARDRAILS_API_KEY": GUARDRAILS_API_KEY,
    "TAVILY_API_KEY": TAVILY_API_KEY,
}

missing = [k for k, v in _required.items() if not v]
if missing:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(missing)}\n"
        "Check your .env file in the project root."
    )
