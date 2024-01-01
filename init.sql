-- Create the 'curly_carnival' database
CREATE DATABASE IF NOT EXISTS curly_carnival;

-- Switch to the 'curly_carnival' database
USE curly_carnival;

-- Create the 'Users' table
CREATE TABLE IF NOT EXISTS Users (
    PhoneNumber VARCHAR(50),
    Email VARCHAR(50),
    UserName VARCHAR(50),
    ThreadID VARCHAR(50),
    GmailToken JSON
);

-- Create the 'Emails' table
CREATE TABLE IF NOT EXISTS Emails (
    ID VARCHAR(50)
);

-- Display a message indicating successful creation
SELECT 'SQL Tables created' AS Message;