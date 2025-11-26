#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Migration Script: Add Conversations Support
Run this to add conversation tracking to PromptSense
"""

import sys
import io
from services.db_service import DatabaseService
import logging

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Run the conversations migration"""
    print("=" * 60)
    print("PromptSense Conversations Migration")
    print("=" * 60)
    print()

    try:
        db = DatabaseService()
        conn = db.get_connection()
        cur = conn.cursor()

        print("📊 Reading migration SQL...")
        with open('models/migration_conversations.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()

        print("🔄 Running migration...")
        cur.execute(migration_sql)
        conn.commit()

        print("✅ Migration completed successfully!")
        print()
        print("New features added:")
        print("  - conversations table created")
        print("  - messages.conversation_id column added")
        print("  - Existing messages migrated to default conversations")
        print("  - Auto-update triggers configured")
        print()

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        logger.exception("Migration error")
        sys.exit(1)


if __name__ == '__main__':
    run_migration()
