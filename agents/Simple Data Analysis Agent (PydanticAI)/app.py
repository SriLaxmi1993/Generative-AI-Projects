"""
Command Line Interface for Data Analysis Agent

Simple CLI for interacting with the data analysis agent.
Supports CSV file input and interactive Q&A.

Author: [Your Name]
Built with: PydanticAI
"""

from __future__ import annotations

import argparse
import os

import pandas as pd
from dotenv import load_dotenv

from src.agent import Deps, build_agent
from src.data import make_car_sales_df


def ask(question: str, df: pd.DataFrame) -> str:
    agent = build_agent()
    deps = Deps(df=df)
    result = agent.run_sync(question, deps=deps)
    # Access the response data - try different methods
    try:
        # Try .data first (common in PydanticAI)
        return str(result.data)
    except AttributeError:
        try:
            # Try new_messages() approach
            return result.new_messages()[-1].content
        except (AttributeError, IndexError):
            # Fallback to string representation
            return str(result)


def main() -> int:
    load_dotenv()
    os.environ.setdefault("LOGFIRE_IGNORE_NO_CONFIG", "1")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        return 1

    parser = argparse.ArgumentParser(description="Simple Data Analysis Agent (PydanticAI)")
    parser.add_argument("--csv", help="Path to a CSV to analyze instead of the synthetic dataset.")
    args = parser.parse_args()

    df = pd.read_csv(args.csv) if args.csv else make_car_sales_df()

    print("=" * 60)
    print("Simple Data Analysis Agent (PydanticAI)")
    print("Built with PydanticAI Framework")
    print("=" * 60)
    print("\nData analysis agent is ready.")
    print("Try: 'What are the column names?', 'How many rows?', 'What is the average Price?'")
    print("Type 'exit' to quit.\n")

    while True:
        q = input("Question> ").strip()
        if not q:
            continue
        if q.lower() in {"exit", "quit"}:
            return 0
        print(f"Answer: {ask(q, df)}\n")


if __name__ == "__main__":
    raise SystemExit(main())

