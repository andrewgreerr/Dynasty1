# This file only needs to be run once per seaon to build the SQLITE3 database with the current year's player information

import sqlite3
import json

# Connect to database (create if not pre-existing)
def create_database():
    conn = sqlite3.connect('players.db')
    cursor = conn.cursor()

    # Builds columns in the table
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


# Populates the created database
def insert_data(json_file):
    conn = sqlite3.connect('players.db')
    cursor = conn.cursor()

    with open(json_file, 'r') as f:
        data = json.load(f)

    # Grabs information for each player, if information is not given 'NA' is put in place | -1 is put in place if age is not available
    for player_id, attributes in data.items():
        first_name = attributes.get('first_name', 'NA')
        last_name = attributes.get('last_name', 'NA')
        age = attributes.get('age', -1)
        position = attributes.get('position', 'NA')

        # Populates database with information or placeholder values
        cursor.execute('''
        INSERT OR REPLACE INTO players (player_id, first_name, last_name, age, position)
        VALUES (?, ?, ?, ?, ?)
        ''', (player_id, first_name, last_name, age, position))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_database()
    insert_data('data.json')
