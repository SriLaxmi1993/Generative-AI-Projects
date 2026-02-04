"""
Data Analysis Agent - Core Agent Definition

This module defines the PydanticAI agent for data analysis with pandas DataFrames.
Built with PydanticAI framework.

Author: [Your Name]
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import pandas as pd
from pydantic_ai import Agent, ModelRetry, RunContext


@dataclass
class Deps:
    """Agent dependencies (injected into tools / prompts)."""

    df: pd.DataFrame


SYSTEM_PROMPT = """You are an AI assistant that helps extract information from a pandas DataFrame.
If asked about columns, check the column names first.
Be concise.

You have access to a tool that can evaluate limited pandas expressions over a DataFrame named `df`.
"""


async def df_query(ctx: RunContext[Deps], query: str) -> str:
    """Run a pandas expression against the injected DataFrame.

    The expression is evaluated via `pandas.eval` with `df` available in scope.
    """
    print(f"Running query: `{query}`")

    # Tiny guardrails: keep the model inside "pandas-on-df" land.
    lowered = query.lower()
    blocked = ["__", "import", "exec", "open(", "os.", "sys.", "subprocess", "socket", "pickle"]
    if any(b in lowered for b in blocked):
        raise ModelRetry("Unsafe query detected. Use pandas operations on `df` only.")

    try:
        result = pd.eval(query, local_dict={"df": ctx.deps.df}, engine="python")
        return str(result)
    except Exception as e:
        raise ModelRetry(f"query: `{query}` is not a valid query. Reason: `{e}`") from e


def build_agent() -> Agent[Deps, str]:
    """Build and configure the agent with tools."""
    model = os.getenv("PYDANTICAI_MODEL", "openai:gpt-4o-mini")
    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        deps_type=Deps,
        retries=10,
    )
    # Register the tool
    agent.tool(df_query)
    return agent


# Agent will be initialized lazily in streamlit_app.py after env vars are loaded
agent: Agent[Deps, str] | None = None

