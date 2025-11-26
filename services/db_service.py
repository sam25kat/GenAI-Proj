import psycopg2
from psycopg2.extras import RealDictCursor, Json
from typing import List, Dict, Optional
from config import Config
import logging
import json

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for Postgres database operations"""

    def __init__(self):
        self.connection_string = Config.DATABASE_URL

    def get_connection(self):
        """Get a database connection"""
        try:
            conn = psycopg2.connect(self.connection_string)
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        "SELECT * FROM users WHERE id = %s",
                        (user_id,)
                    )
                    user = cur.fetchone()
                    return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        "SELECT * FROM users WHERE email = %s",
                        (email,)
                    )
                    user = cur.fetchone()
                    return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error fetching user by email: {e}")
            return None

    def save_message(
        self,
        user_id: int,
        role: str,
        content: str,
        conversation_id: Optional[int] = None,
        original_prompt: Optional[str] = None,
        enhanced_prompt: Optional[str] = None,
        intent: Optional[str] = None,
        domain: Optional[str] = None,
        vector_saved: bool = False,
        metadata: Optional[Dict] = None
    ) -> Optional[int]:
        """Save a message to database"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO messages
                        (user_id, role, content, conversation_id, original_prompt, enhanced_prompt,
                         intent, domain, vector_saved, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (user_id, role, content, conversation_id, original_prompt, enhanced_prompt,
                         intent, domain, vector_saved, Json(metadata or {}))
                    )
                    message_id = cur.fetchone()[0]
                    conn.commit()
                    return message_id
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return None

    def get_user_history(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict]:
        """Get user's message history"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT * FROM messages
                        WHERE user_id = %s
                        ORDER BY timestamp DESC
                        LIMIT %s OFFSET %s
                        """,
                        (user_id, limit, offset)
                    )
                    messages = cur.fetchall()
                    return [dict(msg) for msg in messages]
        except Exception as e:
            logger.error(f"Error fetching user history: {e}")
            return []

    def get_recent_context(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get recent conversation context for a user"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT role, content, intent, domain, timestamp
                        FROM messages
                        WHERE user_id = %s
                        ORDER BY timestamp DESC
                        LIMIT %s
                        """,
                        (user_id, limit)
                    )
                    messages = cur.fetchall()
                    return [dict(msg) for msg in reversed(messages)]
        except Exception as e:
            logger.error(f"Error fetching recent context: {e}")
            return []

    def mark_vector_saved(self, message_id: int) -> bool:
        """Mark a message as having its vector saved"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE messages SET vector_saved = TRUE WHERE id = %s",
                        (message_id,)
                    )
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Error marking vector as saved: {e}")
            return False

    def get_user_domains(self, user_id: int, limit: int = 10) -> List[str]:
        """Get most common domains for a user"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT domain, COUNT(*) as count
                        FROM messages
                        WHERE user_id = %s AND domain IS NOT NULL
                        GROUP BY domain
                        ORDER BY count DESC
                        LIMIT %s
                        """,
                        (user_id, limit)
                    )
                    domains = cur.fetchall()
                    return [domain[0] for domain in domains]
        except Exception as e:
            logger.error(f"Error fetching user domains: {e}")
            return []

    def update_user_preferences(self, user_id: int, preferences: Dict) -> bool:
        """Update user preferences"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE users
                        SET preferences = %s
                        WHERE id = %s
                        """,
                        (json.dumps(preferences), user_id)
                    )
                    conn.commit()
                    return cur.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False

    def initialize_database(self):
        """Initialize database with schema"""
        try:
            with open('models/schema.sql', 'r') as f:
                schema = f.read()

            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(schema)
                    conn.commit()
                    logger.info("Database initialized successfully")
                    return True
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return False

    # Conversation Management Methods

    def create_conversation(self, user_id: int, title: str = 'New Conversation') -> Optional[int]:
        """Create a new conversation"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO conversations (user_id, title)
                        VALUES (%s, %s)
                        RETURNING id
                        """,
                        (user_id, title)
                    )
                    conversation_id = cur.fetchone()[0]
                    conn.commit()
                    return conversation_id
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return None

    def get_user_conversations(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get all conversations for a user"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT c.id, c.title, c.created_at, c.updated_at,
                               COUNT(m.id) as message_count
                        FROM conversations c
                        LEFT JOIN messages m ON c.id = m.conversation_id
                        WHERE c.user_id = %s
                        GROUP BY c.id
                        ORDER BY c.updated_at DESC
                        LIMIT %s
                        """,
                        (user_id, limit)
                    )
                    conversations = cur.fetchall()
                    result = []
                    for conv in conversations:
                        conv_dict = dict(conv)
                        # Convert timestamps to ISO format
                        if conv_dict.get('created_at'):
                            conv_dict['created_at'] = conv_dict['created_at'].isoformat()
                        if conv_dict.get('updated_at'):
                            conv_dict['updated_at'] = conv_dict['updated_at'].isoformat()
                        result.append(conv_dict)
                    return result
        except Exception as e:
            logger.error(f"Error fetching conversations: {e}")
            return []

    def get_conversation_messages(self, conversation_id: int) -> List[Dict]:
        """Get all messages in a conversation"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT * FROM messages
                        WHERE conversation_id = %s
                        ORDER BY timestamp ASC
                        """,
                        (conversation_id,)
                    )
                    messages = cur.fetchall()
                    result = []
                    for msg in messages:
                        msg_dict = dict(msg)
                        # Convert timestamp to ISO format
                        if msg_dict.get('timestamp'):
                            msg_dict['timestamp'] = msg_dict['timestamp'].isoformat()
                        result.append(msg_dict)
                    return result
        except Exception as e:
            logger.error(f"Error fetching conversation messages: {e}")
            return []

    def update_conversation_title(self, conversation_id: int, title: str) -> bool:
        """Update conversation title"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE conversations SET title = %s WHERE id = %s",
                        (title, conversation_id)
                    )
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Error updating conversation title: {e}")
            return False

    def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation and all its messages"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM conversations WHERE id = %s",
                        (conversation_id,)
                    )
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False
