#!/usr/bin/env python3
"""Manually send a report to Slack, bypassing SSL issues if possible."""
import ssl
import os
from slack_integration import SlackReporter
from database import IntelligenceDB

# Try to disable SSL verification (not recommended for production, but for testing)
ssl._create_default_https_context = ssl._create_unverified_context

def send_report():
    """Send intelligence report to Slack."""
    print("\n" + "="*70)
    print("📤 SENDING REPORT TO SLACK")
    print("="*70)
    
    try:
        slack = SlackReporter()
        db = IntelligenceDB()
        
        # Get recent items
        items = db.get_recent_items(days=7)
        
        if not items:
            print("❌ No items to report. Run the agent first: python3 crew.py")
            return
        
        print(f"\n📊 Found {len(items)} intelligence items to report")
        
        # Send daily digest
        print("\n📧 Sending daily digest to Slack...")
        success = slack.send_daily_digest()
        
        if success:
            print("✅ Report sent successfully to Slack!")
            print(f"   Check your Slack channel: {os.getenv('SLACK_CHANNEL_ID')}")
        else:
            print("❌ Failed to send report")
            print("   This might be due to:")
            print("   - SSL certificate issues (system-level)")
            print("   - Incorrect Slack Channel ID")
            print("   - Bot doesn't have permission to post")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Alternative: View results in terminal:")
        print("   python3 view_results.py")
    
    print("="*70)

if __name__ == "__main__":
    send_report()

