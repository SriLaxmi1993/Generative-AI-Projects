"""Slack integration for sending intelligence reports."""
import json
from typing import Dict, Any, List
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID
from database import IntelligenceDB


class SlackReporter:
    """Handles sending intelligence reports to Slack."""
    
    def __init__(self):
        """Initialize Slack client."""
        self.client = WebClient(token=SLACK_BOT_TOKEN)
        self.channel_id = SLACK_CHANNEL_ID
        self.db = IntelligenceDB()
    
    def send_message(self, text: str, blocks: List[Dict] = None) -> bool:
        """Send a message to Slack."""
        try:
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                text=text,
                blocks=blocks
            )
            return response["ok"]
        except SlackApiError as e:
            print(f"Error sending Slack message: {e.response['error']}")
            return False
    
    def format_high_priority_alert(self, item: Dict[str, Any]) -> List[Dict]:
        """Format a high-priority item as a Slack alert."""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 High Priority Intelligence Alert",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Competitor:*\n{item.get('competitor_name', 'Unknown')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Priority:*\n🔴 HIGH"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{item.get('title', 'No title')}*\n\n{item.get('content', 'No description')}"
                }
            }
        ]
        
        if item.get('url'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🔗 <{item['url']}|View Source>"
                }
            })
        
        blocks.append({"type": "divider"})
        
        return blocks
    
    def send_immediate_alert(self, items: List[Dict[str, Any]]) -> bool:
        """Send immediate alert for high-priority items."""
        if not items:
            return True
        
        for item in items:
            blocks = self.format_high_priority_alert(item)
            success = self.send_message(
                text=f"High Priority Alert: {item.get('title', 'New intelligence item')}",
                blocks=blocks
            )
            
            if success:
                # Mark as reported
                self.db.mark_items_reported([item['id']])
        
        return True
    
    def format_daily_digest(self, items: List[Dict[str, Any]]) -> List[Dict]:
        """Format daily digest."""
        from datetime import datetime
        
        # Group by priority
        high_priority = [i for i in items if i.get('priority') == 'High']
        medium_priority = [i for i in items if i.get('priority') == 'Medium']
        low_priority = [i for i in items if i.get('priority') == 'Low']
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 Daily Intelligence Digest - {datetime.now().strftime('%B %d, %Y')}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Total Items:* {len(items)} | 🔴 {len(high_priority)} High | 🟡 {len(medium_priority)} Medium | 🟢 {len(low_priority)} Low"
                }
            },
            {"type": "divider"}
        ]
        
        # Add high priority items
        if high_priority:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🔴 High Priority Items*"
                }
            })
            for item in high_priority[:5]:  # Limit to 5
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{item.get('competitor_name')}*: {item.get('title')}\n{item.get('content', '')[:200]}...\n<{item.get('url', '#')}|Read more>"
                    }
                })
        
        # Add medium priority items
        if medium_priority:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🟡 Medium Priority Items*"
                }
            })
            for item in medium_priority[:5]:  # Limit to 5
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{item.get('competitor_name')}*: {item.get('title')}\n<{item.get('url', '#')}|View>"
                    }
                })
        
        # Add low priority summary
        if low_priority:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🟢 Low Priority Items*\n{len(low_priority)} informational items tracked"
                }
            })
        
        return blocks
    
    def send_daily_digest(self) -> bool:
        """Send daily digest of unreported items."""
        items = self.db.get_unreported_items()
        
        if not items:
            # Send empty digest
            self.send_message(
                text="📊 Daily Intelligence Digest - No new items today",
                blocks=[{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "📊 *Daily Intelligence Digest*\n\nNo new competitive intelligence items today."
                    }
                }]
            )
            return True
        
        blocks = self.format_daily_digest(items)
        success = self.send_message(
            text=f"Daily Intelligence Digest - {len(items)} items",
            blocks=blocks
        )
        
        if success:
            # Mark all as reported
            item_ids = [item['id'] for item in items]
            self.db.mark_items_reported(item_ids)
            
            # Save report
            self.db.save_report("daily", json.dumps(blocks), len(items))
        
        return success
    
    def format_weekly_report(self, items: List[Dict[str, Any]]) -> List[Dict]:
        """Format weekly report."""
        from datetime import datetime, timedelta
        from collections import Counter
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Group by competitor
        competitor_counts = Counter([i.get('competitor_name') for i in items])
        
        # Group by priority
        priority_counts = Counter([i.get('priority') for i in items])
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📈 Weekly Intelligence Report",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Period:* {start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📊 Summary*\n• Total Items: {len(items)}\n• High Priority: {priority_counts.get('High', 0)}\n• Medium Priority: {priority_counts.get('Medium', 0)}\n• Low Priority: {priority_counts.get('Low', 0)}"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏢 Activity by Competitor*\n" + "\n".join([f"• {comp}: {count} items" for comp, count in competitor_counts.most_common()])
                }
            }
        ]
        
        # Add top items
        high_priority = [i for i in items if i.get('priority') == 'High']
        if high_priority:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🔥 Top Highlights*"
                }
            })
            for item in high_priority[:5]:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{item.get('competitor_name')}*: {item.get('title')}\n{item.get('content', '')[:150]}...\n<{item.get('url', '#')}|Read more>"
                    }
                })
        
        return blocks
    
    def send_weekly_report(self) -> bool:
        """Send weekly report."""
        items = self.db.get_recent_items(days=7)
        
        if not items:
            self.send_message(
                text="📈 Weekly Intelligence Report - No items this week",
                blocks=[{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "📈 *Weekly Intelligence Report*\n\nNo competitive intelligence items this week."
                    }
                }]
            )
            return True
        
        blocks = self.format_weekly_report(items)
        success = self.send_message(
            text=f"Weekly Intelligence Report - {len(items)} items",
            blocks=blocks
        )
        
        if success:
            self.db.save_report("weekly", json.dumps(blocks), len(items))
        
        return success
