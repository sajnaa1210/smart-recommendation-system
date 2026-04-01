"""
Database module for user data persistence
Supports both JSON file (local development) and SQLite (production/Vercel)
"""
import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import threading

class DatabaseManager:
    """Manages user data storage"""
    
    def __init__(self, use_sqlite=None):
        """
        Initialize database manager
        
        Args:
            use_sqlite: If True, use SQLite. If None, auto-detect from environment.
        """
        # Auto-detect: use SQLite on Vercel, JSON file locally
        if use_sqlite is None:
            use_sqlite = os.getenv('VERCEL') is not None or os.getenv('DATABASE_URL') is not None
        
        self.use_sqlite = use_sqlite
        self._lock = threading.Lock()
        
        if self.use_sqlite:
            self.db_path = '/tmp/users.db'  # Vercel's /tmp directory
            self._init_sqlite()
        else:
            # Use a persistent JSON file instead of in-memory dict
            self.json_path = os.path.join('data', 'users.json')
            self._ensure_json_file()
    
    def _ensure_json_file(self):
        """Ensure the users JSON file exists"""
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
        if not os.path.exists(self.json_path):
            with open(self.json_path, 'w') as f:
                json.dump({}, f)
    
    def _read_json(self):
        """Read all users from JSON file"""
        try:
            with open(self.json_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _write_json(self, data):
        """Write all users to JSON file"""
        with open(self.json_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _init_sqlite(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL,
                    favourite_books TEXT,
                    liked_books TEXT,
                    viewed_books TEXT,
                    completed_books TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not initialize SQLite: {e}")
            self.use_sqlite = False  # Fallback to JSON file
            self.json_path = os.path.join('data', 'users.json')
            self._ensure_json_file()
    
    def get_user(self, username):
        """Get user by username"""
        if self.use_sqlite:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    return dict(row)
                return None
            except Exception as e:
                print(f"Error reading user: {e}")
                return None
        else:
            with self._lock:
                users = self._read_json()
                return users.get(username)
    
    def set_user(self, username, user_data):
        """Create or update user"""
        if self.use_sqlite:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (username, email, password, favourite_books, liked_books, viewed_books, completed_books)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    username,
                    user_data.get('email'),
                    user_data.get('password'),
                    json.dumps(user_data.get('favourite_books', [])),
                    json.dumps(user_data.get('liked_books', [])),
                    json.dumps(user_data.get('viewed_books', [])),
                    json.dumps(user_data.get('completed_books', []))
                ))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error writing user: {e}")
        else:
            with self._lock:
                users = self._read_json()
                users[username] = user_data
                self._write_json(users)
    
    def user_exists(self, username):
        """Check if user exists"""
        if self.use_sqlite:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
                exists = cursor.fetchone() is not None
                conn.close()
                return exists
            except Exception as e:
                print(f"Error checking user existence: {e}")
                return False
        else:
            with self._lock:
                users = self._read_json()
                return username in users
    
    def get_all_users(self):
        """Get all users (for debugging)"""
        if self.use_sqlite:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users')
                rows = cursor.fetchall()
                conn.close()
                return {row['username']: dict(row) for row in rows}
            except Exception as e:
                print(f"Error reading all users: {e}")
                return {}
        else:
            with self._lock:
                return self._read_json().copy()

# Create global database instance
db = DatabaseManager()

