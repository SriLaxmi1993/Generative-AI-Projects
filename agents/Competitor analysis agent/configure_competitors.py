#!/usr/bin/env python3
"""Helper script to configure competitors and test the setup."""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def show_current_config():
    """Display current configuration."""
    print("\n" + "="*70)
    print("📋 CURRENT CONFIGURATION")
    print("="*70)
    
    competitors = os.getenv("COMPETITORS", "").split(",")
    keywords = os.getenv("KEYWORDS", "").split(",")
    
    print(f"\n🔍 Competitors to track:")
    if competitors and competitors[0] and competitors[0] != "competitor1":
        for i, comp in enumerate(competitors, 1):
            print(f"   {i}. {comp.strip()}")
    else:
        print("   ⚠️  Using placeholder values (competitor1, competitor2, competitor3)")
        print("   Please update your .env file with real competitor names!")
    
    print(f"\n🔑 Keywords to monitor:")
    if keywords and keywords[0] and keywords[0] != "keyword1":
        for i, kw in enumerate(keywords, 1):
            print(f"   {i}. {kw.strip()}")
    else:
        print("   ⚠️  Using placeholder values (keyword1, keyword2, keyword3)")
        print("   Please update your .env file with real keywords!")
    
    # Check API keys
    print(f"\n🔐 API Configuration:")
    print(f"   OpenAI API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
    print(f"   SerpAPI Key: {'✅ Set' if os.getenv('SERPAPI_API_KEY') else '❌ Missing'}")
    print(f"   Twitter Bearer Token: {'✅ Set' if os.getenv('TWITTER_BEARER_TOKEN') else '❌ Missing'}")
    print(f"   Slack Bot Token: {'✅ Set' if os.getenv('SLACK_BOT_TOKEN') else '❌ Missing'}")
    print(f"   Slack Channel ID: {'✅ Set' if os.getenv('SLACK_CHANNEL_ID') else '❌ Missing'}")
    
    print("\n" + "="*70)

def show_how_to_configure():
    """Show instructions on how to configure."""
    print("\n" + "="*70)
    print("📝 HOW TO CONFIGURE COMPETITORS")
    print("="*70)
    print("""
1. Open the .env file in the 'Competitor analysis agent' directory

2. Update the COMPETITORS line with real competitor names (comma-separated):
   Example:
   COMPETITORS=OpenAI,Anthropic,Google DeepMind,Mistral AI

3. Update the KEYWORDS line with relevant keywords (comma-separated):
   Example:
   KEYWORDS=AI agents,LLM,generative AI,GPT

4. Verify your Slack configuration:
   - SLACK_BOT_TOKEN: Your Slack bot token (starts with xapp-)
   - SLACK_CHANNEL_ID: The channel ID where reports should be sent
     (To find channel ID: Right-click channel → View channel details → Copy channel ID)

5. Save the .env file and run the agent again:
   python3 crew.py
""")
    print("="*70)

def test_slack():
    """Test Slack integration."""
    from slack_integration import SlackReporter
    
    print("\n" + "="*70)
    print("🧪 TESTING SLACK INTEGRATION")
    print("="*70)
    
    try:
        slack = SlackReporter()
        test_message = "🧪 Test message from Competitor Analysis Agent"
        success = slack.send_message(test_message)
        
        if success:
            print("✅ Slack message sent successfully!")
            print("   Check your Slack channel for the test message.")
        else:
            print("❌ Failed to send Slack message")
            print("   Please check:")
            print("   - SLACK_BOT_TOKEN is correct")
            print("   - SLACK_CHANNEL_ID is correct")
            print("   - Bot has permission to post in the channel")
    except Exception as e:
        print(f"❌ Error testing Slack: {str(e)}")
        print("   Please verify your Slack configuration in .env")
    
    print("="*70)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "test-slack":
            test_slack()
        elif sys.argv[1] == "config":
            show_how_to_configure()
        else:
            print("Usage:")
            print("  python3 configure_competitors.py          # Show current config")
            print("  python3 configure_competitors.py config  # Show how to configure")
            print("  python3 configure_competitors.py test-slack  # Test Slack")
    else:
        show_current_config()
        show_how_to_configure()

