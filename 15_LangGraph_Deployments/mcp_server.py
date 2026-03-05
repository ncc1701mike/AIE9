"""Local MCP server built with FastMCP.

Exposes three utility tools over Streamable HTTP at:
    http://localhost:8000/mcp

Start the server before running your LangGraph graphs:
    pip install "fastmcp>=2.3"
    python mcp_server.py
"""
from __future__ import annotations

import ast
import operator
from typing import Annotated

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Server instance
# ---------------------------------------------------------------------------
mcp = FastMCP("local-toolbelt")

# ---------------------------------------------------------------------------
# Safe arithmetic helpers
# ---------------------------------------------------------------------------
_OPERATORS: dict = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node: ast.AST) -> float:
    """Recursively evaluate a parsed arithmetic AST node (no exec/eval)."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"Unsupported expression node: {ast.dump(node)}")


# ---------------------------------------------------------------------------
# Tool 1: Summarise text
# ---------------------------------------------------------------------------
@mcp.tool(
    description=(
        "Summarise a block of text to approximately `max_sentences` sentences "
        "using extractive summarisation. Returns the condensed version."
    )
)
def summarize_text(
    text: Annotated[str, "The text to summarise."],
    max_sentences: Annotated[
        int, "Target number of sentences in the summary (default 3)."
    ] = 3,
) -> str:
    import re

    if not text.strip():
        return "No text provided."
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(sentences[:max_sentences])


# ---------------------------------------------------------------------------
# Tool 2: Safe arithmetic evaluator
# ---------------------------------------------------------------------------
@mcp.tool(
    description=(
        "Safely evaluate a mathematical expression and return the numeric result. "
        "Supports +, -, *, /, **, %, //. Does NOT execute arbitrary Python code."
    )
)
def calculate(
    expression: Annotated[str, "A mathematical expression, e.g. '(3 + 4) * 2 ** 3'."],
) -> str:
    try:
        tree = ast.parse(expression.strip(), mode="eval")
        result = _safe_eval(tree)
        return str(int(result)) if result == int(result) else str(result)
    except ZeroDivisionError:
        return "Error: division by zero."
    except Exception as exc:
        return f"Error evaluating expression: {exc}"


# ---------------------------------------------------------------------------
# Tool 3: Weather lookup (mock — swap body for real API in production)
# ---------------------------------------------------------------------------
@mcp.tool(
    description=(
        "Return current weather conditions for a given city. "
        "Swap the mock implementation for a real API call (e.g. OpenWeatherMap) "
        "in production by replacing the body of this function."
    )
)
def fetch_weather(
    city: Annotated[str, "The city name, e.g. 'London'."],
    units: Annotated[
        str, "Temperature units: 'metric' (°C) or 'imperial' (°F). Default 'metric'."
    ] = "metric",
) -> str:
    # --- Replace this block with a real HTTP call in production ---
    # import httpx, os
    # url = "https://api.openweathermap.org/data/2.5/weather"
    # params = {"q": city, "units": units, "appid": os.environ["OWM_API_KEY"]}
    # resp = httpx.get(url, params=params, timeout=10)
    # resp.raise_for_status()
    # data = resp.json()
    # temp = data["main"]["temp"]
    # desc = data["weather"][0]["description"]
    # unit_label = "°C" if units == "metric" else "°F"
    # return f"{city.title()}: {desc}, {temp}{unit_label}"
    # --------------------------------------------------------------
    unit_label = "°C" if units == "metric" else "°F"
    mock: dict[str, tuple[str, int]] = {
        "london":   ("overcast clouds", 12),
        "new york": ("clear sky", 22),
        "tokyo":    ("light rain", 18),
        "sydney":   ("sunny", 25),
        "paris":    ("partly cloudy", 15),
    }
    key = city.strip().lower()
    if key not in mock:
        return f"No weather data found for '{city}'."
    description, temp = mock[key]
    return f"{city.title()}: {description}, {temp}{unit_label}."


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Serves on http://localhost:8000/mcp  (Streamable HTTP — MCP spec 2025-03-26)
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)