import mysql.connector

mydb = mysql.connector.connect(
    user="me",
    password="pass",
    database="test"
)

print(mydb)