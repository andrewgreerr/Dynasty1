import sqlite3
import json


def create_database():
    """Create the database and table with the specified columns."""
    conn = sqlite3.connect('players.db')
    cursor = conn.cursor()

    # Create the table with only the required columns
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        player_id TEXT PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        age INTEGER,
        position TEXT
    )
    ''')

    conn.commit()
    conn.close()


def insert_data(json_file):
    """Insert data from JSON file into the database with placeholder values for missing columns."""
    conn = sqlite3.connect('players.db')
    cursor = conn.cursor()

    # Load JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)

    for player_id, attributes in data.items():
        # Extract only the required fields, with default values if missing
        first_name = attributes.get('first_name', 'NA')
        last_name = attributes.get('last_name', 'NA')
        age = attributes.get('age', -1)
        position = attributes.get('position', 'NA')

        # Insert or replace into the database
        cursor.execute('''
        INSERT OR REPLACE INTO players (player_id, first_name, last_name, age, position)
        VALUES (?, ?, ?, ?, ?)
        ''', (player_id, first_name, last_name, age, position))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_database()
    insert_data('data.json')
