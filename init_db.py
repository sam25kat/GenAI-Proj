#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Database Initialization Script for PromptSense
Run this script to set up the database schema and demo users
"""

import sys
import io
from services.db_service import DatabaseService
from config import Config
import logging

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize the database"""
    print("=" * 60)
    print("PromptSense Database Initialization")
    print("=" * 60)
    print()

    # Check configuration
    if not Config.DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not configured in .env file")
        print("Please add your Postgres Neon connection string to .env")
        sys.exit(1)

    print(f"📊 Database: {Config.DATABASE_URL.split('@')[1] if '@' in Config.DATABASE_URL else 'configured'}")
    print()

    # Confirm
    response = input("Initialize database? This will create tables and demo users (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)

    print()
    print("🔄 Initializing database...")

    try:
        db = DatabaseService()
        success = db.initialize_database()

        if success:
            print("✅ Database initialized successfully!")
            print()
            print("Demo users created:")
            print("  1. Demo User (ID: 1) - Beginner level, friendly tone")
            print("  2. Advanced User (ID: 2) - Advanced level, professional tone")
            print()
            print("You can now run the application with: python app.py")
        else:
            print("❌ Database initialization failed. Check the logs above.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        logger.exception("Database initialization error")
        sys.exit(1)


if __name__ == '__main__':
    main()
