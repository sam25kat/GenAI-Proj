import psycopg2
from psycopg2.extras import RealDictCursor, Json
from typing import List, Dict, Optional
from config import Config
import logging

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
                        (user_id, role, content, original_prompt, enhanced_prompt,
                         intent, domain, vector_saved, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (user_id, role, content, original_prompt, enhanced_prompt,
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
