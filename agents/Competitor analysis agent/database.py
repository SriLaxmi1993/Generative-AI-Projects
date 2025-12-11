"""Database management for competitive intelligence data."""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import os
from config import DATABASE_PATH


class IntelligenceDB:
    """Manages SQLite database for competitive intelligence storage."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialize database connection and create tables if needed."""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Create database tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Competitors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS competitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                website TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Intelligence items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS intelligence_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_id INTEGER,
                source TEXT NOT NULL,
                source_type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                url TEXT,
                priority TEXT NOT NULL,
                metadata TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reported BOOLEAN DEFAULT 0,
                FOREIGN KEY (competitor_id) REFERENCES competitors(id)
            )
        """)
        
        # Social activity table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS social_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_id INTEGER,
                platform TEXT NOT NULL,
                activity_type TEXT,
                content TEXT,
                engagement_score INTEGER,
                url TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (competitor_id) REFERENCES competitors(id)
            )
        """)
        
        # Reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_type TEXT NOT NULL,
                content TEXT NOT NULL,
                items_count INTEGER,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Changes tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS change_detection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_id INTEGER,
                change_type TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (competitor_id) REFERENCES competitors(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_competitor(self, name: str, website: str = None) -> int:
        """Add a new competitor to track."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO competitors (name, website) VALUES (?, ?)",
                (name, website)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Competitor already exists, get its ID
            cursor.execute("SELECT id FROM competitors WHERE name = ?", (name,))
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def get_competitor_id(self, name: str) -> Optional[int]:
        """Get competitor ID by name."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM competitors WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def add_intelligence_item(
        self,
        competitor_name: str,
        source: str,
        source_type: str,
        title: str,
        content: str,
        url: str,
        priority: str,
        metadata: Dict[str, Any] = None
    ) -> int:
        """Add a new intelligence item."""
        competitor_id = self.get_competitor_id(competitor_name)
        if not competitor_id:
            competitor_id = self.add_competitor(competitor_name)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO intelligence_items 
            (competitor_id, source, source_type, title, content, url, priority, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            competitor_id,
            source,
            source_type,
            title,
            content,
            url,
            priority,
            json.dumps(metadata) if metadata else None
        ))
        
        conn.commit()
        item_id = cursor.lastrowid
        conn.close()
        return item_id
    
    def add_social_activity(
        self,
        competitor_name: str,
        platform: str,
        activity_type: str,
        content: str,
        engagement_score: int,
        url: str,
        metadata: Dict[str, Any] = None
    ) -> int:
        """Add social media activity."""
        competitor_id = self.get_competitor_id(competitor_name)
        if not competitor_id:
            competitor_id = self.add_competitor(competitor_name)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO social_activity 
            (competitor_id, platform, activity_type, content, engagement_score, url, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            competitor_id,
            platform,
            activity_type,
            content,
            engagement_score,
            url,
            json.dumps(metadata) if metadata else None
        ))
        
        conn.commit()
        activity_id = cursor.lastrowid
        conn.close()
        return activity_id
    
    def get_unreported_items(self, priority: str = None) -> List[Dict[str, Any]]:
        """Get intelligence items that haven't been reported yet."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT i.*, c.name as competitor_name
            FROM intelligence_items i
            JOIN competitors c ON i.competitor_id = c.id
            WHERE i.reported = 0
        """
        
        if priority:
            query += " AND i.priority = ?"
            cursor.execute(query, (priority,))
        else:
            cursor.execute(query)
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def mark_items_reported(self, item_ids: List[int]):
        """Mark intelligence items as reported."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(item_ids))
        cursor.execute(
            f"UPDATE intelligence_items SET reported = 1 WHERE id IN ({placeholders})",
            item_ids
        )
        
        conn.commit()
        conn.close()
    
    def save_report(self, report_type: str, content: str, items_count: int) -> int:
        """Save a generated report."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO reports (report_type, content, items_count)
            VALUES (?, ?, ?)
        """, (report_type, content, items_count))
        
        conn.commit()
        report_id = cursor.lastrowid
        conn.close()
        return report_id
    
    def get_recent_items(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get intelligence items from the last N days."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT i.*, c.name as competitor_name
            FROM intelligence_items i
            JOIN competitors c ON i.competitor_id = c.id
            WHERE i.discovered_at >= datetime('now', '-' || ? || ' days')
            ORDER BY i.discovered_at DESC
        """, (days,))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def detect_change(
        self,
        competitor_name: str,
        change_type: str,
        old_value: str,
        new_value: str
    ) -> int:
        """Record a detected change."""
        competitor_id = self.get_competitor_id(competitor_name)
        if not competitor_id:
            competitor_id = self.add_competitor(competitor_name)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO change_detection 
            (competitor_id, change_type, old_value, new_value)
            VALUES (?, ?, ?, ?)
        """, (competitor_id, change_type, old_value, new_value))
        
        conn.commit()
        change_id = cursor.lastrowid
        conn.close()
        return change_id
