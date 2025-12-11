#!/usr/bin/env python3
"""View stored intelligence results from the database."""
from database import IntelligenceDB
from datetime import datetime

def view_all_items():
    """Display all stored intelligence items."""
    db = IntelligenceDB()
    
    # Get all items
    items = db.get_recent_items(days=365)  # Get all items from last year
    
    print("\n" + "="*70)
    print("📊 STORED INTELLIGENCE ITEMS")
    print("="*70)
    
    if not items:
        print("\n📭 No intelligence items found in database.")
        print("   Run 'python3 crew.py' to gather intelligence first.")
        print("="*70)
        return
    
    # Group by priority
    high_priority = [i for i in items if i.get('priority') == 'High']
    medium_priority = [i for i in items if i.get('priority') == 'Medium']
    low_priority = [i for i in items if i.get('priority') == 'Low']
    
    print(f"\n📈 Summary:")
    print(f"   Total Items: {len(items)}")
    print(f"   🔴 High Priority: {len(high_priority)}")
    print(f"   🟡 Medium Priority: {len(medium_priority)}")
    print(f"   🟢 Low Priority: {len(low_priority)}")
    
    # Display high priority items
    if high_priority:
        print("\n" + "-"*70)
        print("🔴 HIGH PRIORITY ITEMS")
        print("-"*70)
        for idx, item in enumerate(high_priority, 1):
            print(f"\n{idx}. {item.get('competitor_name', 'Unknown')}")
            print(f"   Title: {item.get('title', 'No title')}")
            print(f"   Source: {item.get('source', 'Unknown')}")
            if item.get('url'):
                print(f"   URL: {item.get('url')}")
            if item.get('content'):
                content = item.get('content', '')[:200]
                print(f"   Summary: {content}...")
            if item.get('created_at'):
                print(f"   Date: {item.get('created_at')}")
    
    # Display medium priority items
    if medium_priority:
        print("\n" + "-"*70)
        print("🟡 MEDIUM PRIORITY ITEMS")
        print("-"*70)
        for idx, item in enumerate(medium_priority[:10], 1):  # Show first 10
            print(f"\n{idx}. {item.get('competitor_name', 'Unknown')}")
            print(f"   Title: {item.get('title', 'No title')}")
            if item.get('url'):
                print(f"   URL: {item.get('url')}")
    
    # Display low priority summary
    if low_priority:
        print("\n" + "-"*70)
        print(f"🟢 LOW PRIORITY ITEMS ({len(low_priority)} items)")
        print("-"*70)
        print(f"   {len(low_priority)} informational items tracked")
    
    print("\n" + "="*70)
    print("💡 Tip: Use 'python3 configure_competitors.py' to configure competitors")
    print("="*70)

if __name__ == "__main__":
    view_all_items()

