# database.py
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json

class Database:
    def __init__(self, db_path: str):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        print(f"Using database: {db_path}")
        self.init_db()
    
    def init_db(self) -> None:
        """Create necessary database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    model TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    last_updated TIMESTAMP NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    file_id INTEGER,
                    FOREIGN KEY (chat_id) REFERENCES chats (id),
                    FOREIGN KEY (file_id) REFERENCES attachments (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    content BLOB NOT NULL,
                    uploaded_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (chat_id) REFERENCES chats (id)
                )
            """)
    
    def create_chat(self, title: str, model: str) -> int:
        """
        Create a new chat and return its ID.
        
        Args:
            title (str): Chat title
            model (str): Model used for the chat
            
        Returns:
            int: The ID of the newly created chat
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute(
                """
                INSERT INTO chats (title, model, created_at, last_updated)
                VALUES (?, ?, ?, ?)
                """,
                (title, model, now, now)
            )
            return cursor.lastrowid
    
    def save_message(self, chat_id: int, role: str, content: str, file_id: int = None) -> None:
        """
        Save a message to the database and prune old messages if necessary.
        
        Args:
            chat_id (int): ID of the chat
            role (str): Message role (user/assistant)
            content (str): Message content
        """
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.now().isoformat()
            conn.execute(
                """
                INSERT INTO messages (chat_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (chat_id, role, content, now)
            )
            conn.execute(
                """
                UPDATE chats SET last_updated = ? WHERE id = ?
                """,
                (now, chat_id)
            )
            
            # Prune old messages if history exceeds limit
            from config import Config
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*) FROM messages WHERE chat_id = ?
                """,
                (chat_id,)
            )
            count = cursor.fetchone()[0]
            
            if count > Config.MAX_HISTORY_LENGTH:
                # Calculate how many messages to delete
                to_delete = count - Config.MAX_HISTORY_LENGTH
                cursor.execute(
                    """
                    DELETE FROM messages
                    WHERE id IN (
                        SELECT id FROM messages
                        WHERE chat_id = ?
                        ORDER BY timestamp ASC
                        LIMIT ?
                    )
                    """,
                    (chat_id, to_delete)
                )
    
    def get_all_chats(self) -> List[Dict]:
        """
        Get all chats ordered by last updated time.
        
        Returns:
            List[Dict]: List of chat dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, title, model, created_at, last_updated
                FROM chats
                ORDER BY last_updated DESC
                """
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_chat_messages(self, chat_id: int) -> List[Dict]:
        """
        Get all messages for a specific chat with attachment info.
        
        Args:
            chat_id (int): ID of the chat
            
        Returns:
            List[Dict]: List of message dictionaries with attachment info
        """
        """
        Get all messages for a specific chat.
        
        Args:
            chat_id (int): ID of the chat
            
        Returns:
            List[Dict]: List of message dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT role, content
                FROM messages
                WHERE chat_id = ?
                ORDER BY timestamp ASC
                """,
                (chat_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_chat(self, chat_id: int) -> Optional[Dict]:
        """
        Get chat details by ID.
        
        Args:
            chat_id (int): ID of the chat
            
        Returns:
            Optional[Dict]: Chat details or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, title, model, created_at, last_updated
                FROM chats
                WHERE id = ?
                """,
                (chat_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def delete_chat(self, chat_id: int) -> None:
        """
        Delete a chat and all its messages.
        
        Args:
            chat_id (int): ID of the chat to delete
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
            conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    
    def update_chat_title(self, chat_id: int, new_title: str) -> None:
        """
        Update the title of a chat.
        
        Args:
            chat_id (int): ID of the chat
            new_title (str): New title for the chat
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE chats SET title = ?, last_updated = ?
                WHERE id = ?
                """,
                (new_title, datetime.now().isoformat(), chat_id)
            )
    
    def save_attachment(self, chat_id: int, filename: str, content: bytes) -> int:
        """
        Save an uploaded file attachment
        
        Args:
            chat_id (int): ID of the chat
            filename (str): Original filename
            content (bytes): File content
            
        Returns:
            int: Attachment ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute(
                """
                INSERT INTO attachments (chat_id, filename, content, uploaded_at)
                VALUES (?, ?, ?, ?)
                """,
                (chat_id, filename, content, now)
            )
            return cursor.lastrowid

    def clear_all_history(self) -> None:
        """Delete all chat history from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM chats")
                cursor.execute("DELETE FROM messages")
                conn.commit()
                print(f"Deleted {cursor.rowcount} records from chats and messages tables")
        except sqlite3.Error as e:
            print(f"Error clearing history: {e}")
