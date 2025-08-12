# AdminPanel/app/database.py
import sqlite3
from contextlib import contextmanager
from config.telegram_config import TelegramConfig
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AdminDatabase:
    def __init__(self, db_path='admin_panel.db'):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """Managed database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return dict-like rows
        try:
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    is_admin BOOLEAN DEFAULT 0,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP
                )
            ''')
            
            # Activity log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    activity_type TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # System alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_type TEXT NOT NULL,
                    severity TEXT CHECK(severity IN ('low', 'medium', 'high')),
                    message TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP
                )
            ''')
            
            # Insert admin user if not exists
            cursor.execute('''
                INSERT OR IGNORE INTO users 
                (user_id, username, first_name, is_admin)
                VALUES (?, ?, ?, 1)
            ''', (TelegramConfig.ADMIN_ID, "admin", "Admin"))
            
            conn.commit()

    # User Management
    def add_user(self, user_data):
        """Add new user to database"""
        with self._get_connection() as conn:
            conn.execute('''
                INSERT INTO users 
                (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (
                user_data['id'],
                user_data.get('username', ''),
                user_data.get('first_name', ''),
                user_data.get('last_name', '')
            ))
            conn.commit()
        logger.info(f"Added new user: {user_data['id']}")

    def log_activity(self, user_id, activity_type, details=None, ip=None):
        """Record user activity"""
        with self._get_connection() as conn:
            conn.execute('''
                INSERT INTO activity_log 
                (user_id, activity_type, details, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (user_id, activity_type, details, ip))
            
            # Update last active timestamp
            conn.execute('''
                UPDATE users 
                SET last_active = ?
                WHERE user_id = ?
            ''', (datetime.now(), user_id))
            
            conn.commit()
        logger.debug(f"Logged activity: {user_id} - {activity_type}")

    # Alert Management
    def create_alert(self, alert_type, message, severity='medium'):
        """Create new system alert"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alerts 
                (alert_type, severity, message)
                VALUES (?, ?, ?)
            ''', (alert_type, severity, message))
            alert_id = cursor.lastrowid
            conn.commit()
        logger.warning(f"New alert created: {alert_type} (ID: {alert_id})")
        return alert_id

    def get_unresolved_alerts(self):
        """Get all unresolved alerts"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM alerts 
                WHERE resolved = 0 
                ORDER BY created_at DESC
            ''')
            return cursor.fetchall()

    # Utility Methods
    def get_user(self, user_id):
        """Get user by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            return cursor.fetchone()

    def get_recent_activities(self, limit=10):
        """Get recent system activities"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM activity_log 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()

# Database instance for import
db = AdminDatabase()

# Example usage:
if __name__ == '__main__':
    # Initialize logger
    logging.basicConfig(level=logging.DEBUG)
    
    # Test database operations
    test_user = {
        'id': 123456,
        'username': 'test_user',
        'first_name': 'Test'
    }
    
    db.add_user(test_user)
    db.log_activity(123456, 'login', 'Successful login')
    alert_id = db.create_alert('test', 'This is a test alert')
    print(f"Created alert with ID: {alert_id}")
    
    print("\nRecent activities:")
    for activity in db.get_recent_activities(5):
        print(f"{activity['timestamp']} - {activity['activity_type']}")