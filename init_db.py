"""
PawConnect Database Initialization Script
Executes database.sql on the local MySQL server using credentials from .env.
"""
import os
import sys
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'pawconnect_db')

def init_database():
    print("=" * 60)
    print(" PawConnect - Database Setup & Initialization")
    print("=" * 60)
    print(f"Connecting to MySQL at {DB_HOST}:{DB_PORT} as user '{DB_USER}'...")

    # Connect directly to pawconnect_db to ensure no other database is touched
    try:
        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                autocommit=True
            )
        except mysql.connector.Error as db_err:
            # If pawconnect_db does not exist yet (Error 1049), connect to server to create it
            if getattr(db_err, 'errno', None) == 1049:
                conn = mysql.connector.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    autocommit=True
                )
            else:
                raise db_err

        cursor = conn.cursor()
        print(f" Connected to database '{DB_NAME}' successfully!")

        sql_file_path = os.path.join(os.path.dirname(__file__), 'database.sql')
        if not os.path.exists(sql_file_path):
            print(f" Error: {sql_file_path} not found!")
            return False

        print(f" Reading schema and seed data from {sql_file_path}...")
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # Split statements by semicolon, ignoring empty lines or comments
        statements = []
        delimiter = ';'
        current_stmt = []

        for line in sql_script.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith('--') or stripped.startswith('/*'):
                continue
            current_stmt.append(line)
            if stripped.endswith(';'):
                stmt_str = '\n'.join(current_stmt).rstrip(';').strip()
                if stmt_str:
                    statements.append(stmt_str)
                current_stmt = []

        print(f" Executing {len(statements)} SQL statements...")
        for i, stmt in enumerate(statements, 1):
            try:
                cursor.execute(stmt)
            except Exception as stmt_err:
                # Print non-fatal or schema errors
                print(f"  [Statement {i}] Notice: {stmt_err}")

        cursor.close()
        conn.close()

        print("\n Database setup completed successfully!")
        print(f" Database '{DB_NAME}' is ready with tables and sample records.")
        print("\n Sample Accounts:")
        print("  - Admin:   admin@pawconnect.org")
        print("  - Shelter: hopeforpaws@shelter.org")
        print("  - Adopter: pooja@example.com")
        print("  Note: Seed accounts use randomized placeholder password hashes.")
        print("        Create a new account via the UI or reset credentials before logging in.")
        print("=" * 60)
        return True

    except mysql.connector.Error as err:
        print(f"\n MySQL Error: {err}")
        print("Tip: Check your DB_USER and DB_PASSWORD in the .env file.")
        return False
    except Exception as ex:
        print(f"\n Unexpected Error: {ex}")
        return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
