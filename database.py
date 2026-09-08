# ==========================================
# Database Connection
# Environment Monitoring System
# ==========================================

import mysql.connector

from config import *

# ==========================================
# Connect Database
# ==========================================

def get_connection():

    return mysql.connector.connect(

        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME

    )

# ==========================================
# Execute Query
# ==========================================

def execute_query(query, values=None):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(query, values)

    conn.commit()

    cursor.close()

    conn.close()

# ==========================================
# Fetch One Record
# ==========================================

def fetch_one(query, values=None):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(query, values)

    data = cursor.fetchone()

    conn.close()

    return data

# ==========================================
# Fetch All Records
# ==========================================

def fetch_all(query, values=None):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(query, values)

    data = cursor.fetchall()

    conn.close()

    return data