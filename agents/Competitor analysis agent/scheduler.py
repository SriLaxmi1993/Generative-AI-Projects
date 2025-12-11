"""Scheduler for automated competitive intelligence runs."""
import schedule
import time
from datetime import datetime
from crew import CompetitiveIntelligenceCrew
from config import DAILY_RUN_TIME, WEEKLY_REPORT_DAY, WEEKLY_REPORT_TIME


def run_daily_intelligence():
    """Run daily intelligence gathering and send digest."""
    print(f"\n{'='*60}")
    print(f"🕐 Daily Intelligence Run - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    crew = CompetitiveIntelligenceCrew()
    
    # Run intelligence gathering
    results = crew.run_intelligence_gathering()
    
    # Send daily digest
    crew.send_daily_digest()
    
    print(f"\n{'='*60}")
    print(f"✅ Daily run complete - {results['total_items']} items processed")
    print(f"{'='*60}\n")


def send_weekly_report():
    """Send weekly intelligence report."""
    print(f"\n{'='*60}")
    print(f"📈 Weekly Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    crew = CompetitiveIntelligenceCrew()
    crew.send_weekly_report()
    
    print(f"\n{'='*60}")
    print(f"✅ Weekly report sent")
    print(f"{'='*60}\n")


def main():
    """Main scheduler loop."""
    print("🚀 Starting Competitive Intelligence Scheduler")
    print(f"📅 Daily runs scheduled for: {DAILY_RUN_TIME}")
    print(f"📅 Weekly reports scheduled for: {WEEKLY_REPORT_DAY.capitalize()} at {WEEKLY_REPORT_TIME}")
    print("="*60)
    
    # Schedule daily intelligence gathering at 9am
    schedule.every().day.at(DAILY_RUN_TIME).do(run_daily_intelligence)
    
    # Schedule weekly report on Friday at 5pm
    getattr(schedule.every(), WEEKLY_REPORT_DAY).at(WEEKLY_REPORT_TIME).do(send_weekly_report)
    
    print("✅ Scheduler started. Press Ctrl+C to stop.\n")
    
    # Run immediately on startup (optional - comment out if not desired)
    print("🔄 Running initial intelligence gathering...")
    run_daily_intelligence()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Scheduler stopped by user")
    except Exception as e:
        print(f"\n\n❌ Scheduler error: {str(e)}")
