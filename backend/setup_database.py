#!/usr/bin/env python
"""
Database Setup Script for SQL Migrator
Allows easy configuration and testing of different database connections.

Usage:
    python setup_database.py --type sqlite          # SQLite file-based
    python setup_database.py --type postgresql      # PostgreSQL local default
    python setup_database.py --type mysql           # MySQL local default
    python setup_database.py --type oracle          # Oracle local default
    python setup_database.py --custom               # Custom configuration wizard
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def setup_sqlite():
    """Setup file-based SQLite database."""
    db_path = "backend/database/app_data.db"
    uri = f"sqlite:///{db_path.replace(chr(92), '/')}"
    
    print("\n" + "="*70)
    print("SQLITE DATABASE CONFIGURATION")
    print("="*70)
    print(f"Database File: {db_path}")
    print(f"Connection URI: {uri}")
    
    # Create database directory
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    print("✓ Database directory created/verified")
    
    return uri

def setup_postgresql():
    """Setup PostgreSQL database."""
    host = input("PostgreSQL Host (default: localhost): ").strip() or "localhost"
    port = input("PostgreSQL Port (default: 5432): ").strip() or "5432"
    database = input("Database Name (default: sql_migrator): ").strip() or "sql_migrator"
    username = input("Username (default: postgres): ").strip() or "postgres"
    password = input("Password (default: postgres): ").strip() or "postgres"
    
    uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
    
    print("\n" + "="*70)
    print("POSTGRESQL DATABASE CONFIGURATION")
    print("="*70)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database: {database}")
    print(f"Username: {username}")
    print(f"Connection URI: {uri}")
    
    return uri

def setup_mysql():
    """Setup MySQL database."""
    host = input("MySQL Host (default: localhost): ").strip() or "localhost"
    port = input("MySQL Port (default: 3306): ").strip() or "3306"
    database = input("Database Name (default: sql_migrator): ").strip() or "sql_migrator"
    username = input("Username (default: root): ").strip() or "root"
    password = input("Password (default: root): ").strip() or "root"
    
    uri = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    
    print("\n" + "="*70)
    print("MYSQL DATABASE CONFIGURATION")
    print("="*70)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database: {database}")
    print(f"Username: {username}")
    print(f"Connection URI: {uri}")
    
    return uri

def setup_oracle():
    """Setup Oracle database."""
    host = input("Oracle Host (default: localhost): ").strip() or "localhost"
    port = input("Oracle Port (default: 1521): ").strip() or "1521"
    service_name = input("Service Name (default: xe): ").strip() or "xe"
    username = input("Username (default: system): ").strip() or "system"
    password = input("Password (default: oracle): ").strip() or "oracle"
    
    uri = f"oracle+cx_oracle://{username}:{password}@{host}:{port}/?service_name={service_name}"
    
    print("\n" + "="*70)
    print("ORACLE DATABASE CONFIGURATION")
    print("="*70)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Service Name: {service_name}")
    print(f"Username: {username}")
    print(f"Connection URI: {uri}")
    
    return uri

def update_env_file(uri):
    """Update .env file with new database URI."""
    env_file = ".env"
    
    # Read existing .env
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Replace or add SQLALCHEMY_DATABASE_URI
        if "SQLALCHEMY_DATABASE_URI=" in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("SQLALCHEMY_DATABASE_URI="):
                    lines[i] = f"SQLALCHEMY_DATABASE_URI={uri}"
                    break
            content = '\n'.join(lines)
        else:
            content += f"\n\nSQLALCHEMY_DATABASE_URI={uri}\n"
    else:
        content = f"SQLALCHEMY_DATABASE_URI={uri}\n"
    
    # Write back to .env
    with open(env_file, 'w') as f:
        f.write(content)
    
    print(f"✓ Updated .env file with new database configuration")

def test_connection(uri):
    """Test database connection."""
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(uri, echo=False)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ Database connection successful!")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def init_tables():
    """Initialize database tables."""
    try:
        from backend.app import create_app
        from backend.extensions import db
        
        print("\nInitializing database tables...")
        app = create_app()
        
        with app.app_context():
            db.create_all()
            print("✓ Database tables created successfully!")
            
            # List tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"\nTables created: {', '.join(tables)}")
            
            return True
    except Exception as e:
        print(f"✗ Failed to initialize tables: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="SQL Migrator Database Setup")
    parser.add_argument("--type", choices=["sqlite", "postgresql", "mysql", "oracle"],
                       help="Database type to configure")
    parser.add_argument("--custom", action="store_true", help="Custom configuration")
    parser.add_argument("--test", action="store_true", help="Test connection only")
    parser.add_argument("--init", action="store_true", help="Initialize database tables")
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("SQL MIGRATOR - DATABASE SETUP")
    print("="*70)
    
    if args.test:
        # Test mode - read from .env
        if os.path.exists(".env"):
            from dotenv import load_dotenv
            load_dotenv()
            uri = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
            print(f"\nTesting connection to: {uri[:50]}...")
            test_connection(uri)
        return
    
    # Determine database type
    if args.type == "sqlite":
        uri = setup_sqlite()
    elif args.type == "postgresql":
        uri = setup_postgresql()
    elif args.type == "mysql":
        uri = setup_mysql()
    elif args.type == "oracle":
        uri = setup_oracle()
    else:
        # Interactive mode
        print("\nSelect database type:")
        print("1. SQLite (file-based, recommended for development)")
        print("2. PostgreSQL")
        print("3. MySQL")
        print("4. Oracle")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            uri = setup_sqlite()
        elif choice == "2":
            uri = setup_postgresql()
        elif choice == "3":
            uri = setup_mysql()
        elif choice == "4":
            uri = setup_oracle()
        else:
            print("Invalid choice")
            return
    
    # Update .env file
    update_env_file(uri)
    
    # Test connection
    if test_connection(uri):
        # Initialize tables
        if input("\nInitialize database tables? (y/n): ").lower() == 'y':
            init_tables()
    
    print("\n" + "="*70)
    print("✓ DATABASE SETUP COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. Restart the backend server (it will reload with new configuration)")
    print("2. The backend will use the configured database automatically")
    print("\nTo restart the backend:")
    print("  cd backend")
    print("  py app.py")
    print()

if __name__ == "__main__":
    main()
