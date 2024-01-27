import mysql.connector

mydb = mysql.connector.connect(
    user="root",
    password="pass",
    host="172.17.0.2"
)

print(mydb)