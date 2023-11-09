import os
from dotenv import load_dotenv
from assistant import Assistant


def main():
    load_dotenv()
    id = os.getenv("ASSISTANT_ID")
    user = os.getenv("FIRST_NAME") + " " + os.getenv("LAST_NAME")