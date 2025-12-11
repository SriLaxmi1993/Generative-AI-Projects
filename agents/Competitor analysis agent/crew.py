"""Main crew orchestration for competitive intelligence."""
from crewai import Crew, Process
from agents import (
    create_web_researcher_agent,
    create_social_monitor_agent,
    create_analyst_agent,
    create_slack_reporter_agent
)
from tasks import (
    create_web_research_task,
    create_social_monitoring_task,
    create_analysis_task,
    create_reporting_task
)
from database import IntelligenceDB
from slack_integration import SlackReporter
from config import COMPETITORS, KEYWORDS, PRIORITY_HIGH_KEYWORDS
import json
from typing import Dict, Any


class CompetitiveIntelligenceCrew:
    """Orchestrates the competitive intelligence crew."""
    
    def __init__(self):
        """Initialize the crew."""
        self.db = IntelligenceDB()
        self.slack = SlackReporter()
        
        # Create agents
        self.web_researcher = create_web_researcher_agent()
        self.social_monitor = create_social_monitor_agent()
        self.analyst = create_analyst_agent()
        self.slack_reporter = create_slack_reporter_agent()
    
    def run_intelligence_gathering(self) -> Dict[str, Any]:
        """Run the intelligence gathering process."""
        print("🔍 Starting competitive intelligence gathering...")
        
        # Create tasks
        web_research_task = create_web_research_task(
            self.web_researcher,
            competitors=COMPETITORS
        )
        
        social_monitoring_task = create_social_monitoring_task(
            self.social_monitor,
            competitors=COMPETITORS,
            keywords=KEYWORDS
        )
        
        analysis_task = create_analysis_task(
            self.analyst,
            web_research_task,
            social_monitoring_task
        )
        
        # Create crew for intelligence gathering
        crew = Crew(
            agents=[
                self.web_researcher,
                self.social_monitor,
                self.analyst
            ],
            tasks=[
                web_research_task,
                social_monitoring_task,
                analysis_task
            ],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute crew
        result = crew.kickoff()
        
        print("✅ Intelligence gathering complete!")
        return self._process_results(result)
    
    def _process_results(self, result: Any) -> Dict[str, Any]:
        """Process crew results and store in database."""
        print("💾 Processing and storing results...")
        
        try:
            # Parse the analysis result
            if isinstance(result, str):
                # Remove markdown code blocks if present
                cleaned_result = result.strip()
                if cleaned_result.startswith('```json'):
                    cleaned_result = cleaned_result[7:]  # Remove ```json
                if cleaned_result.startswith('```'):
                    cleaned_result = cleaned_result[3:]  # Remove ```
                if cleaned_result.endswith('```'):
                    cleaned_result = cleaned_result[:-3]  # Remove closing ```
                cleaned_result = cleaned_result.strip()
                analysis_data = json.loads(cleaned_result)
            else:
                analysis_data = result
            
            # Extract intelligence items
            items = []
            if isinstance(analysis_data, dict):
                # Try different possible structures
                if 'intelligence_items' in analysis_data:
                    # Handle nested structure: intelligence_items.HIGH, intelligence_items.MEDIUM, etc.
                    intel_items = analysis_data['intelligence_items']
                    if isinstance(intel_items, dict):
                        items.extend(intel_items.get('HIGH', []))
                        items.extend(intel_items.get('MEDIUM', []))
                        items.extend(intel_items.get('LOW', []))
                    else:
                        items = intel_items
                elif 'high_priority' in analysis_data:
                    items.extend(analysis_data.get('high_priority', []))
                elif 'medium_priority' in analysis_data:
                    items.extend(analysis_data.get('medium_priority', []))
                elif 'low_priority' in analysis_data:
                    items.extend(analysis_data.get('low_priority', []))
                elif 'items' in analysis_data:
                    items = analysis_data['items']
                elif 'findings' in analysis_data:
                    items = analysis_data['findings']
            
            # Store items in database
            high_priority_items = []
            
            for item in items:
                # Extract fields
                competitor = item.get('competitor', 'Unknown')
                title = item.get('title', 'No title')
                content = item.get('summary', item.get('content', ''))
                priority = item.get('priority', 'Low')
                source = item.get('source', 'Unknown')
                url = item.get('url', '')
                
                # Determine source type
                source_type = 'web'
                if 'twitter' in source.lower():
                    source_type = 'twitter'
                elif 'hacker news' in source.lower():
                    source_type = 'hackernews'
                elif 'product hunt' in source.lower():
                    source_type = 'producthunt'
                
                # Store in database
                item_id = self.db.add_intelligence_item(
                    competitor_name=competitor,
                    source=source,
                    source_type=source_type,
                    title=title,
                    content=content,
                    url=url,
                    priority=priority,
                    metadata=item
                )
                
                # Track high priority items (case-insensitive check)
                if priority.upper() == 'HIGH':
                    item['id'] = item_id
                    item['competitor_name'] = competitor
                    high_priority_items.append(item)
            
            print(f"✅ Stored {len(items)} intelligence items")
            print(f"🔴 Found {len(high_priority_items)} high-priority items")
            
            # Send immediate alerts for high-priority items
            if high_priority_items:
                print("📢 Sending immediate alerts for high-priority items...")
                self.slack.send_immediate_alert(high_priority_items)
            
            return {
                'total_items': len(items),
                'high_priority': len(high_priority_items),
                'items': items
            }
        
        except Exception as e:
            print(f"❌ Error processing results: {str(e)}")
            print(f"Raw result: {result}")
            return {
                'total_items': 0,
                'high_priority': 0,
                'items': [],
                'error': str(e)
            }
    
    def send_daily_digest(self):
        """Send daily digest of intelligence."""
        print("📊 Sending daily digest...")
        self.slack.send_daily_digest()
        print("✅ Daily digest sent!")
    
    def send_weekly_report(self):
        """Send weekly intelligence report."""
        print("📈 Sending weekly report...")
        self.slack.send_weekly_report()
        print("✅ Weekly report sent!")


def main():
    """Main entry point for running the crew."""
    crew = CompetitiveIntelligenceCrew()
    
    # Run intelligence gathering
    results = crew.run_intelligence_gathering()
    
    print("\n" + "="*70)
    print("📊 INTELLIGENCE GATHERING SUMMARY")
    print("="*70)
    print(f"✅ Total items found: {results['total_items']}")
    print(f"🔴 High priority items: {results['high_priority']}")
    
    if results.get('items'):
        print("\n📋 DETAILED FINDINGS:")
        print("-" * 70)
        for idx, item in enumerate(results['items'][:10], 1):  # Show first 10
            priority_emoji = "🔴" if item.get('priority') == 'High' else "🟡" if item.get('priority') == 'Medium' else "🟢"
            print(f"\n{idx}. {priority_emoji} [{item.get('priority', 'Unknown')}] {item.get('competitor', 'Unknown')}")
            print(f"   Title: {item.get('title', 'No title')}")
            if item.get('url'):
                print(f"   URL: {item.get('url')}")
    
    if results.get('error'):
        print(f"\n⚠️  Warning: {results['error']}")
    
    print("="*70)


if __name__ == "__main__":
    main()
