"""
Script to print all user data from the SQLite database file (db.sqlite3).
Run this from the Randomwalk directory using: python print_users.py
"""

import sqlite3
import os
import sys


def print_all_users():
    """Print all user submissions directly from the SQLite database."""
    
    # Path to the database file
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Query all users from the mailinglist_submission table
        cursor.execute("SELECT id, username, email FROM mailinglist_submission")
        submissions = cursor.fetchall()
        
        if not submissions:
            print("No users found in the database.")
            return
        
        print(f"\n{'='*60}")
        print(f"Total Users: {len(submissions)}")
        print(f"{'='*60}\n")
        
        for idx, (user_id, username, email) in enumerate(submissions, 1):
            print(f"User #{idx}")
            print(f"  ID: {user_id}")
            print(f"  Username: {username}")
            print(f"  Email: {email}")
            print(f"{'-'*60}")
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    
    finally:
        conn.close()


if __name__ == "__main__":
    print_all_users()
