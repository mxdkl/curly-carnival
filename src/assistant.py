import os
import time
import json
from dotenv import load_dotenv
from openaiAPI import OpenAIWrapper
from gmailAPI import GmailWrapper
from greenAPI import GreenApiWrapper
from database import Database


class Assistant(OpenAIWrapper, GmailWrapper, Database):
    def __init__(self, id):
        OpenAIWrapper.__init__(self)
        GmailWrapper.__init__(self)
        Database.__init__(self)

        # Here is the key changes
        self.greenApi = GreenApiWrapper()
        self.greenApi.recipient = self

        self.id = id

    def chat(self, thread_id, message: str, attachments: list = []):
        # Create message
        self._createMessage(thread_id, message, attachments)

        # Run assistant
        run = self._createRun(thread_id)

        # Wait for assistant to finish. This code jank af
        while run.status != "completed":
            if run.status == "requires_action":
                outputs = []
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    if tool_call.type == "function":
                        # Run function called by assistant
                        arguments = json.loads(tool_call.function.arguments)
                        function_name = tool_call.function.name
                        output = str(self._callFunctionByName(function_name, arguments))
                        outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": output
                        })
                self._submitRunToolOutput(thread_id, run.id, outputs)
            elif run.status == "failed" or run.status == "cancelled":
                print("Error occurred while running assistant.")
                return

            time.sleep(1)
            run = self._retrieveRun(thread_id, run.id)
            
        # Retrieve assistant response
        response = self.client.beta.threads.messages.list(thread_id).data[0].content[0].text.value
        return response

    def _createMessage(self, thread_id, message, file_ids = []):
        thread_message = self.client.beta.threads.messages.create(
            thread_id,
            role = "user",
            content = message,
            file_ids = file_ids
        )
        return thread_message
    
    def _createThread(self):
        thread = self.client.beta.threads.create()
        return thread.id

    
    def _createRun(self, thread_id):
        run = self.client.beta.threads.runs.create(
            thread_id = thread_id,
            assistant_id = self.id
        )
        return run
    
    def _retrieveRun(self, thread_id, run_id):
        run = self.client.beta.threads.runs.retrieve(
            thread_id = thread_id,
            run_id = run_id
        )
        return run
    
    def _submitRunToolOutput(self, thread_id, run_id, outputs):
        run = self.client.beta.threads.runs.submit_tool_outputs(
            thread_id = thread_id,
            run_id = run_id,
            tool_outputs = outputs
        )
        return run
    
    def _callFunctionByName(self, function_name, arguments):
        if hasattr(self, function_name) and callable(getattr(self, function_name)):
            func = getattr(self, function_name)
            func(**arguments)
        else:
            print(f"Function '{function_name}' not found.")

    def getNewMessage(self, data):
        sender = data["senderData"]["sender"]
        message = data["messageData"]["textMessageData"]["textMessage"]
        print(f"New message from {sender}: {message}")
        result = self.searchDatabase("PhoneNumber", sender)
        if len(result) == 0:
            # Create new thread and insert into database
            thread_id = self._createThread()
            self.insertIntoDatabase(PhoneNumber=sender, ThreadID=thread_id)
        else:
            # Get thread id from database
            thread_id = result[0][2]
        response = self.chat(thread_id, message)
        self.greenApi.sendMessage(sender, response)
    

if __name__ == "__main__":
    # Create an assistant
    name = "Eve, Personal Assistant"
    instructions = "You are a helpful assistant. You are a young woman named Eve. You conduct yourself very professionally, which you must because you deal with clients personal information, but can sometimes let your guard down depending on the client."
    description = "Eve is a personal assistant that helps you with your daily tasks."
    model = "gpt-4-1106-preview"
    tools = []
    with open('assistant-tools.json') as f:
        tools = json.load(f)
    id = OpenAIWrapper.createAssistant(name=name, description=description, instructions=instructions, model=model, tools=tools, files=None)