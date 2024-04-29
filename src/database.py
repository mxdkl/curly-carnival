import os
from dotenv import load_dotenv
import mysql.connector
from time import sleep

# Not a general database class. Scope is limited to this project.


class Database:
    def __init__(self, max_retries=5, retry_interval=5):
        self.max_retries = max_retries
        self.retry_interval = retry_interval

        # Load environment variables
        load_dotenv()

        # Connect to the database with retry logic
        self.mydb = self.connect_with_retry()

        # Create a cursor
        self.mycursor = self.mydb.cursor()

        # Increase wait_timeout and interactive_timeout
        self.mycursor.execute("SET SESSION wait_timeout = 100000")
        self.mycursor.execute("SET SESSION interactive_timeout = 100000")

    def connect_with_retry(self):
        retries = 0
        while retries < self.max_retries:
            try:
                # Attempt to connect to the database
                mydb = mysql.connector.connect(
                    user=os.getenv("MYSQL_USER"),
                    password=os.getenv("MYSQL_PASSWORD"),
                    host=os.getenv("MYSQL_HOST"),
                    database=os.getenv("MYSQL_DATABASE"),
                    port=3306,
                )
                return mydb
            except mysql.connector.Error as err:
                print(f"Error connecting to MySQL: {err}")
                retries += 1
                if retries < self.max_retries:
                    print(f"Retrying in {self.retry_interval} seconds...")
                    sleep(self.retry_interval)
                else:
                    print("Exceeded maximum retries. Exiting.")
                    exit(1)

    def searchDatabase(self, column, value):
        self.mycursor.execute(
            f"SELECT * FROM Users WHERE {column} = '{value}'")
        rows = self.mycursor.fetchall()
        column_names = [desc[0] for desc in self.mycursor.description]
        rows = [dict(zip(column_names, row)) for row in rows]
        return rows

    def registerPhoneNumber(self, user_id, phone_number, thread_id):
        # add new phone number to database
        self.mycursor.execute(f"INSERT INTO Users (UserID, PhoneNumber, ThreadID) VALUES ('{
                              user_id}', '{phone_number}', '{thread_id}')")
        self.mydb.commit()

    def registerEmail(self, user_id, user_name, email, gmail_token):
        # find row with user_id that matches and add user_name, email, and gmail_token
        self.mycursor.execute(f"UPDATE Users SET UserName = '{user_name}', Email = '{
                              email}', GmailToken = '{gmail_token}' WHERE UserID = '{user_id}'")
        self.mydb.commit()
