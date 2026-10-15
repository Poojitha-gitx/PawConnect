"""
PawConnect Database Access Layer
Uses mysql-connector-python with parameterized queries.
"""
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

def get_db_config():
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'pawconnect_db'),
        'charset': 'utf8mb4',
        'use_unicode': True,
        'autocommit': True
    }
    # Optional SSL flag for Cloud MySQL providers (e.g. TiDB, Aiven)
    if os.getenv('DB_SSL', 'false').lower() in ('true', '1', 't', 'required'):
        config['ssl_disabled'] = False
        ssl_ca = os.getenv('DB_SSL_CA')
        if ssl_ca and os.path.exists(ssl_ca):
            config['ssl_ca'] = ssl_ca
    return config

def get_db_connection():
    """Returns a new MySQL database connection."""
    config = get_db_config()
    try:
        conn = mysql.connector.connect(**config)
        return conn
    except Error as e:
        print(f"[Database Connection Error]: {e}")
        raise e

def query_db(query, args=(), one=False):
    """
    Executes a SELECT query using parameterized statements and returns dictionary results.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, args)
        rv = cursor.fetchall()
        return (rv[0] if rv else None) if one else rv
    except Error as e:
        print(f"[Query DB Error]: {e} | Query: {query}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def modify_db(query, args=()):
    """
    Executes an INSERT, UPDATE, or DELETE parameterized statement.
    Returns: (lastrowid, rowcount)
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
        last_id = cursor.lastrowid
        row_count = cursor.rowcount
        return last_id, row_count
    except Error as e:
        if conn and conn.is_connected():
            conn.rollback()
        print(f"[Modify DB Error]: {e} | Query: {query}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def execute_transaction(operations):
    """
    Executes multiple SQL operations in a single atomic transaction.
    operations: list of tuples (query_string, tuple_of_args)
    Returns: list of (lastrowid, rowcount) for each operation
    """
    conn = None
    cursor = None
    results = []
    try:
        conn = get_db_connection()
        conn.autocommit = False
        cursor = conn.cursor()
        for query, args in operations:
            cursor.execute(query, args)
            results.append((cursor.lastrowid, cursor.rowcount))
        conn.commit()
        return results
    except Error as e:
        if conn and conn.is_connected():
            conn.rollback()
        print(f"[Transaction Error]: {e}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
