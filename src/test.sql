CREATE DATABASE IF NOT EXISTS test;
use test;

CREATE TABLE drafts (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    PRIMARY KEY (id)
);

INSERT INTO drafts (name) VALUES ('draft1');