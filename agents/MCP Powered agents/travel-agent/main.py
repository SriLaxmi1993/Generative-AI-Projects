#!/usr/bin/env python3
"""
Main entry point for the Travel Agent
Run this script to interact with the travel planning agent
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  Warning: OPENAI_API_KEY not found in environment or .env file")
    print("Please set your OpenAI API key:")
    print("  1. Create a .env file in this directory")
    print("  2. Add: OPENAI_API_KEY=your_key_here")
    print("\nOr set it as an environment variable:")
    print("  export OPENAI_API_KEY=your_key_here")
    sys.exit(1)

from src.agents.orchestrator import create_orchestrator


def main():
    """Main function to run the travel agent interactively."""
    print("=" * 60)
    print("AI Travel Assistant - Multi-Agent System")
    print("=" * 60)
    print("\nThis agent helps you find Airbnb properties and flight schedules.")
    print("Note: MCP tools work best through Cursor's AI assistant.")
    print("\n" + "-" * 60 + "\n")
    
    # Initialize orchestrator
    try:
        orchestrator = create_orchestrator(model_name="gpt-4")
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        sys.exit(1)
    
    # Interactive mode
    print("Enter your travel query (or 'quit' to exit):\n")
    
    while True:
        try:
            query = input("> ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not query:
                continue
            
            # Run the orchestrator
            result = orchestrator.run(query)
            
            # Display results
            print("\n" + "=" * 60)
            print("RESULTS")
            print("=" * 60)
            print(result.get("summary", "No summary available"))
            print("\n" + "-" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            print()


if __name__ == "__main__":
    main()

