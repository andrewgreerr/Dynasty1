import pandas as pd
import sqlite3

# Step 1: Load the Excel file
excel_file = 'Salary.xlsx'  # Replace with your file name
sheet_name = 'Salary'  # Replace with your sheet name if needed

# Read the Excel file into a pandas DataFrame
df = pd.read_excel(excel_file, sheet_name=sheet_name)

# Step 2: Connect to SQLite Database (or create it)
sqlite_file = 'C:/Users/andre/PycharmProjects/html/PValue.db'  # Replace with your database file name
conn = sqlite3.connect(sqlite_file)

# Step 3: Write the DataFrame to SQLite
table_name = 'player_value'  # Replace with your table name
df.to_sql(table_name, conn, if_exists='replace', index=False)

# Step 4: Close the connection
conn.close()

print(f"Data from {excel_file} has been successfully written to {sqlite_file} in the table {table_name}.")