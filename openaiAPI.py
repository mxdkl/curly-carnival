import os
from dotenv import load_dotenv
import time
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
    
    def _uploadFiles(files):
        file_ids = []
        for file in files:
            pass
        return file_ids
    
class Assistant(OpenAIWrapper):
    def __init__(self, id, user):
        super().__init__()
        self.id = id
        self.user = user
        self.threads = client.beta.threads.create()

    def chat(self, message: str, attachments: list = []):
        self._createMessage(message, attachments)

        # Run assistant
        run = client.beta.threads.runs.create(
            thread_id = self.threads.id,
            assistant_id = self.id
        )

        # Wait for assistant to finish. This code jank af
        while run.status != "completed":
            if run.status == "requires_action":
                outputs = []
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    # Run function called by assistant here
                    outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": 'true'
                    })
                self._submitRunToolOutput(run.id, outputs)

            time.sleep(1)
            run = self._retrieveRun(run.id)
            
        # Retrieve assistant response
        response = client.beta.threads.messages.list(self.threads.id).data
        return response

    def _createMessage(self, message, file_ids = []):
        thread_message = client.beta.threads.messages.create(
            self.threads.id,
            role = "user",
            content = message,
            file_ids = file_ids
        )
        return thread_message
    
    def _retrieveRun(self, run_id):
        run = client.beta.threads.runs.retrieve(
            thread_id = self.threads.id,
            run_id = run_id
        )
        return run
    
    def _submitRunToolOutput(self, run_id, outputs):
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id = self.threads.id,
            run_id = run_id,
            tool_outputs = outputs
        )
        return run
    

if __name__ == "__main__":

    # Create an assistant
    name = "Eve, Personal Assistant"
    instructions = "You are a helpful assistant. You are a young woman named Eve. You conduct yourself very professionally, which you must because you deal with clients personal information, but can sometimes let your guard down depending on the client."
    description = "Eve is a personal assistant that helps you with your daily tasks."
    model = "gpt-4-1106-preview"
    tools = [
        {
            "type": "retrieval"
        },
        {
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
        }
    ]

    # Create assistant
    #id = OpenAIWrapper.createAssistant(name=name, description=description, instructions=instructions, model=model, tools=tools, files=None)

    eve = Assistant(id = os.getenv("ASSISTANT_ID"), user = "test")
    print(eve.chat("send an email to john doe with the subject hello and the body hello world. john doe's email is john@gmail.com"))

