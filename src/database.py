import os
from dotenv import load_dotenv
import mysql.connector


# Not a general database class. Scope is limited to this project.
class Database:
    def __init__(self):
        load_dotenv()
        self.mydb = mysql.connector.connect(
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASS"),
            host = os.getenv("DB_HOST"),
            database = os.getenv("DB_NAME")
        )
        self.mycursor = self.mydb.cursor()

    def searchDatabase(self, column, value):
        self.mycursor.execute(f"SELECT * FROM Users WHERE {column} = '{value}'")
        rows = self.mycursor.fetchall()
        assert len(rows) <= 1, f"Expected 0 or 1 rows, got {len(rows)} rows."
        return rows
    
    def insertIntoDatabase(self, PhoneNumber, ThreadID, Email = None):
        self.mycursor.execute(f"INSERT INTO Users (PhoneNumber, ThreadID, Email) VALUES ('{PhoneNumber}', '{ThreadID}', '{Email}')")
        self.mydb.commit()
