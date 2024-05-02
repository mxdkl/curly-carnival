CREATE DATABASE [IF NOT EXISTS] test;
use test;

-- Create the 'Users' table
CREATE TABLE [IF NOT EXISTS] Users (
    UserID VARCHAR(50),
    UserName VARCHAR(50),
    PhoneNumber VARCHAR(50),
    Email VARCHAR(50),
    ThreadID VARCHAR(50),
    GmailToken TEXT
);

INSERT INTO User (UserName) VALUES ('Jee');

CREATE TABLE [IF NOT EXISTS] drafts (
    draft_id INT AUTO_INCREMENT,
    user_id VARCHAR(50) NOT NULL,
    to TEXT,
    cc TEXT,
    bcc TEXT,
    subject VARCHAR(1000),
    body TEXT,
    PRIMARY KEY (draft_id),
    CONSTRAINT fk_user
    FOREIGN KEY (user_id)
    REFERENCES Users(UserID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

INSERT INTO drafts (body) VALUES ('write something here');