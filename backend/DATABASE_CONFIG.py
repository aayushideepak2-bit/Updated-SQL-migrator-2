"""
Database Connection Parameters for SQL Migrator

This file contains the connection parameters for different database types.
Configure these settings based on your target database.
"""

# ============================================================================
# CURRENT DATABASE (In-Memory SQLite - Development)
# ============================================================================
SQLITE_CONFIG = {
    "type": "sqlite",
    "host": "N/A (File-based or In-Memory)",
    "port": "N/A",
    "database": ":memory:",
    "username": "N/A",
    "password": "N/A",
    "url": "sqlite:///:memory:"
}

# ============================================================================
# POSTGRESQL CONFIGURATION
# ============================================================================
POSTGRESQL_CONFIG = {
    "type": "postgresql",
    "host": "localhost",
    "port": "5432",
    "database": "sql_migrator",
    "username": "postgres",
    "password": "postgres",  # Change this to your actual password
    "url": "postgresql+psycopg2://postgres:postgres@localhost:5432/sql_migrator"
}

# Example with custom credentials:
POSTGRESQL_CUSTOM = {
    "type": "postgresql",
    "host": "your-postgres-host.com",
    "port": "5432",
    "database": "your_database_name",
    "username": "your_username",
    "password": "your_password",
    "url": "postgresql+psycopg2://your_username:your_password@your-postgres-host.com:5432/your_database_name"
}

# ============================================================================
# MYSQL CONFIGURATION
# ============================================================================
MYSQL_CONFIG = {
    "type": "mysql",
    "host": "localhost",
    "port": "3306",
    "database": "sql_migrator",
    "username": "root",
    "password": "root",  # Change this to your actual password
    "url": "mysql+pymysql://root:root@localhost:3306/sql_migrator"
}

# Example with custom credentials:
MYSQL_CUSTOM = {
    "type": "mysql",
    "host": "your-mysql-host.com",
    "port": "3306",
    "database": "your_database_name",
    "username": "your_username",
    "password": "your_password",
    "url": "mysql+pymysql://your_username:your_password@your-mysql-host.com:3306/your_database_name"
}

# ============================================================================
# ORACLE CONFIGURATION
# ============================================================================
ORACLE_CONFIG = {
    "type": "oracle",
    "host": "localhost",
    "port": "1521",
    "service_name": "xe",  # Oracle service name (instead of database)
    "username": "system",
    "password": "oracle",  # Change this to your actual password
    "url": "oracle+cx_oracle://system:oracle@localhost:1521/?service_name=xe"
}

# Example with custom credentials:
ORACLE_CUSTOM = {
    "type": "oracle",
    "host": "your-oracle-host.com",
    "port": "1521",
    "service_name": "your_service_name",
    "username": "your_username",
    "password": "your_password",
    "url": "oracle+cx_oracle://your_username:your_password@your-oracle-host.com:1521/?service_name=your_service_name"
}

# ============================================================================
# USAGE INSTRUCTIONS
# ============================================================================
"""
To use a specific database, update the .env file with the appropriate
SQLALCHEMY_DATABASE_URI value:

For PostgreSQL (local):
    SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://postgres:postgres@localhost:5432/sql_migrator

For MySQL (local):
    SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:root@localhost:3306/sql_migrator

For Oracle (local):
    SQLALCHEMY_DATABASE_URI=oracle+cx_oracle://system:oracle@localhost:1521/?service_name=xe

For SQLite (file-based):
    SQLALCHEMY_DATABASE_URI=sqlite:///backend/database/app_data.db

For SQLite (in-memory):
    SQLALCHEMY_DATABASE_URI=sqlite:///:memory:

Then restart the backend server for the changes to take effect.
"""

# ============================================================================
# CONNECTION PARAMETERS REFERENCE
# ============================================================================

def get_connection_params(database_type: str) -> dict:
    """
    Get connection parameters for a specific database type.
    
    Args:
        database_type: One of 'sqlite', 'postgresql', 'mysql', 'oracle'
    
    Returns:
        Dictionary with connection parameters (host, port, database, username, password)
    """
    configs = {
        'sqlite': SQLITE_CONFIG,
        'postgresql': POSTGRESQL_CONFIG,
        'mysql': MYSQL_CONFIG,
        'oracle': ORACLE_CONFIG,
    }
    return configs.get(database_type.lower(), {})


if __name__ == "__main__":
    # Print all available configurations
    print("\n" + "="*70)
    print("SQL MIGRATOR - DATABASE CONNECTION PARAMETERS")
    print("="*70 + "\n")
    
    configs = [
        ("SQLite (Current)", SQLITE_CONFIG),
        ("PostgreSQL", POSTGRESQL_CONFIG),
        ("MySQL", MYSQL_CONFIG),
        ("Oracle", ORACLE_CONFIG),
    ]
    
    for name, config in configs:
        print(f"\n{name}:")
        print("-" * 70)
        for key, value in config.items():
            print(f"  {key:.<20} {value}")
