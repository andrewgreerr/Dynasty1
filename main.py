from flask import Flask, render_template, jsonify, render_template_string
from bs4 import BeautifulSoup
import requests
import sqlite3

app = Flask(__name__)

extracted_data ={}

# Static dictionary to map HTML file to Team ID 
users = {
    "donnelly.html" : '739542804027531264',
    "greer.html" : '1000545944431063040',
    "trumbull.html" : '1108785220448436224',
    "jackson.html" : '1113616360376082432',
    "julius.html" : '1114212004807409664',
    "shapiro.html" : '1114217268537434112',
    "brian.html" : '1124689612208713728',
    "greg.html" : '1125876560688566272',
    "briggs.html" : '1125876849424453632',
    "gahan.html" : '1125877103204909056',
    "eric.html" : '1125951149175140352',
    "decker.html" : '1127783132725444608'
}

# *** Renewing a Dynasty league on sleeper technically creates a new league and the league ID must be changed for GET requests to be accurate ***

# Gets rosters of league based on our league ID
def fetch_rosters():
    url = 'https://api.sleeper.app/v1/league/1113520351100637184/rosters'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Gets user ID for each memeber of the league
def fetch_users():
    url = 'https://api.sleeper.app/v1/league/1113520351100637184/users'
    response = requests.get(url)
    print(response)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# '/' is the home HTML page, anytime this page is reached it will call the fetch_rosters function to pull newest rosters
@app.route('/')
def serve_html():
    try:
        data = fetch_rosters()
        for roster in data:
            owner_id = roster.get("owner_id")
            players = roster.get("players", [])
            extracted_data[owner_id] = players
        print("extracted data: ", extracted_data)
        return render_template('home.html', rosters=extracted_data)
    except requests.RequestException as e:
        return f"An error occurred: {e}", 500

# Static page to show all values of players 
@app.route('/rawdata.html')
def raw():
    return render_template("rawdata.html")


@app.route('/run-function', methods=['GET'])
def run_function():
    fetch_rosters()
    fetch_users()
    return jsonify({"message": "Python function executed successfully."})


# Dynamic function, takes in the url filename being reach [User's name]
@app.route('/<filename>')
def serve_other_files(filename):
    user_id = users[filename]
    split = filename.split('.')
    print(split[0], " : ", extracted_data[user_id])
    with open("templates/" + filename, 'r', encoding='utf-8') as file:    #Extracts name of user from the url link and reads the HTML that is currently saved
        soup = BeautifulSoup(file, 'html.parser')
        tbody_element = soup.find(('tbody'))        # Finds part section of the HTML that contains the table with the information of the user's roster

        if tbody_element:
            tbody_element.clear()        # Clears out all of the information that is in the table

            conn = sqlite3.connect('players.db')        # Connects to the player information database
            pvalue_conn = sqlite3.connect('PValue.db')        # Connects to the database containing the each player's salary 
            cursor = conn.cursor()
            pvalue_cursor = pvalue_conn.cursor()

            total_age = 0
            total_value = 0
            num_players = len(extracted_data[user_id])

            rows_data = []

            # Loop through all of the user's roster information
            for person in extracted_data[user_id]:
                try:
                    # for each player, retrieve the specified information from player information database
                    cursor.execute('SELECT first_name, last_name, age, position FROM players WHERE player_id = ?',
                                   (person,))

                    row = cursor.fetchone()

                    if row:
                        full_name = f"{row[0]} {row[1]}"        # Combines first and last name to get full name
                        print(f"Querying PValue.db for: {full_name}")
                        pvalue_cursor.execute('SELECT Value FROM player_value WHERE TRIM(Name) = ?', (full_name,))  # searches for player value using full name
                        pvalue_row = pvalue_cursor.fetchone()

                        value = pvalue_row[0] if pvalue_row else 1        # If the player doesn't have a value, they will automatically be given the value of 1
                        total_value += value

                        total_age += row[2]

                        # Store the row data
                        rows_data.append({
                            'full_name': full_name,
                            'position': row[3],
                            'age': row[2],
                            'value': value
                        })

                    else:
                        print(f"No player found with ID {person}")

                except sqlite3.Error as e:
                    print(f"An error occurred: {e}")

            # Sort the rows by value from high to low
            rows_data.sort(key=lambda x: x['value'], reverse=True)

            # Add new entry in the table for each player on the user's roster
            for index, data in enumerate(rows_data, start=1):
                tbody_element.append(BeautifulSoup("<tr>" +
                                                   "<td>" +
                                                   str(index) +
                                                   "</td>" +
                                                   "<td>" +
                                                   data['full_name'] +
                                                   "</td>" +
                                                   "<td>" +
                                                   data['position'] +
                                                   "</td>" +
                                                   "<td>" +
                                                   str(data['age']) +
                                                   "</td>" +
                                                   "<td>" +
                                                   str(data['value']) +
                                                   "</td>" +
                                                   "</tr>", 'html.parser'))

            # Calculate the average age
            average_age = total_age / num_players if num_players > 0 else 0

            # Add the "Average Age" and "Total" rows
            tbody_element.append(BeautifulSoup("<tr>" +
                                               "<td colspan='3'></td>" +
                                               "<td><strong>Average Age</strong></td>" +
                                               "<td colspan='4'><strong>Total</strong></td>" +
                                               "</tr>", 'html.parser'))

            tbody_element.append(BeautifulSoup("<tr>" +
                                               "<td colspan='3'></td>" +
                                               "<td>" + f"{average_age:.2f}" + "</td>" +
                                               "<td>" + f"{total_value}" + "</td>" +
                                               "</tr>", 'html.parser'))

            conn.close()
            pvalue_conn.close()

        else:
            # If <tbody> element is not found, handle it appropriately
            new_ul = soup.new_tag('ul')
            for person in extracted_data[user_id]:
                new_ul.append(BeautifulSoup(person, 'html.parser'))
            soup.body.append(new_ul)

    with open("templates/" + filename, "w", encoding="utf-8") as file:
        file.write(soup.prettify())

    return render_template(filename)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
