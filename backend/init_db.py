#!/usr/bin/env python
"""
Database initialization script for SQL Migrator.
This script creates all database tables and initializes the database.

Usage:
    python init_db.py
"""

import os
import sys

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import create_app
from backend.extensions import db

def init_database():
    """Initialize the database by creating all tables."""
    print("Initializing database...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Drop all tables (WARNING: This deletes all data!)
            # Uncomment only if you want to reset the database
            # db.drop_all()
            # print("Dropped all existing tables.")
            
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully!")
            
            # Show created tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"\nCreated tables ({len(tables)}):")
                for table in tables:
                    columns = inspector.get_columns(table)
                    print(f"  - {table}")
                    for column in columns:
                        col_type = str(column['type'])
                        nullable = "nullable" if column.get('nullable', True) else "NOT NULL"
                        print(f"      • {column['name']}: {col_type} ({nullable})")
            else:
                print("No tables found in database.")
                
        except Exception as e:
            print(f"✗ Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    init_database()
    print("\n✓ Database initialization complete!")
