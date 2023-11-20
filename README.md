## About
An assistant that can
- Send emails

## Requirments
- Python 3.11
- OpenAI api token
- Gmail api token
- Green Whatsapp api token
- Azure api token

## Installation
- Clone the repository
- Run `pip install -r requirements.txt`
- Fill .env file with your tokens
- Set up SQL database
    - `mysql/mairadb -u username -p -h hostname database_name < create_database.sql`
- Create a cron job to run `python3 check_email.py`
- Run `python3 main.py`