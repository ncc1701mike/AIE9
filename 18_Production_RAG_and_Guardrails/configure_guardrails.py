#!/usr/bin/env python3
"""
Workaround script for guardrails configure command.
The guardrails CLI has a bug in version 0.5.14, so use this script instead.

Usage:
    uv run python configure_guardrails.py [API_KEY]

Or set the API key via environment variable:
    export GUARDRAILS_API_KEY=your_api_key_here
    uv run python configure_guardrails.py
"""

import os
import sys
from pathlib import Path


def get_config_path() -> Path:
    """Get the guardrails config file path."""
    home = Path.home()
    # Guardrails stores config in ~/.guardrails/credentials.json
    config_dir = home / ".guardrails"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "credentials.json"


def configure_guardrails(api_key: str):
    """Configure guardrails API key."""
    import json
    
    config_path = get_config_path()
    config = {"api_key": api_key}
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Guardrails API key configured successfully!")
    print(f"   Config saved to: {config_path}")
    print(f"   ⚠️  Keep your API key secret and do not commit it to git!")


def main():
    from config import GUARDRAILS_API_KEY
    
    api_key = GUARDRAILS_API_KEY

    if not api_key:
        print("❌ Error: GUARDRAILS_API_KEY not found in .env")
        sys.exit(1)

    configure_guardrails(api_key)


if __name__ == "__main__":
    main()

