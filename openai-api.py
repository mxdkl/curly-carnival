import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()


class OpenAIWrapper:
    def __init__(self):
        self.api_key = OpenAI.api_key
        self.chat_history = []

    def createAssistant(name, description, instructions, model, tools, files):
        assistant = client.beta.assistants.create(
            name=name,
            instructions=instructions,
            description=description,
            model=model,
            tools=tools,
        )
        return assistant.id

class EveAssistant(OpenAIWrapper):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.threads = client.beta.threads.create(
            messages = []
        )

    def talk(self, message, attachment = None):
        pass

    def _run():
        pass

if __name__ == "__main__":
    name = "Eve, Personal Assistant"
    instructions="You are a helpful assistant. You are a young woman named Eve. You conduct yourself very professionally, which you must because you deal with clients personal information, but can sometimes let your guard down depending on the client."
    description="Eve is a personal assistant that helps you with your daily tasks."
    model="gpt-4-1106-preview"
    tools=[{
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "send an email",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "whom to send the email"
                    },
                    "subject": {
                        "type": "string",
                        "description": "subject of the email"
                    },
                    "body": {
                        "type": "string",
                        "description": "body of the email"
                    }
                },
                "required": [
                    "to",
                    "subject",
                    "body"
                ]
            }
        }
    }]

    id = OpenAIWrapper.createAssistant(name=name, description=description, instructions=instructions, model=model, tools=tools, files=None)

    eve = EveAssistant(id)

