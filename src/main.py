import os
from dotenv import load_dotenv
from assistant import Assistant


def main():
    load_dotenv()
    id = os.getenv("ASSISTANT_ID")

    eve = Assistant(id)
    eve.greenApi.receivingMessage()
    
    while True:
        pass


if __name__ == "__main__":
    main()
