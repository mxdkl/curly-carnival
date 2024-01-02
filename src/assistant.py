import time
import json
import uuid
from openaiAPI import OpenAIWrapper
from gmailAPI import GmailWrapper
from twilioAPI import TwilioApiWrapper
from database import Database


class Assistant(OpenAIWrapper, GmailWrapper, TwilioApiWrapper, Database):
    def __init__(self, name=None, description=None, instructions=None, model=None, tools=None, files=None, id=None):
        OpenAIWrapper.__init__(self)
        GmailWrapper.__init__(self)
        TwilioApiWrapper.__init__(self)
        Database.__init__(self)

        if id:
            self.id = id
        else:
            self.id = self.createAssistant(name=name, description=description, instructions=instructions, model=model, tools=tools, files=files)

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
                        self.service = self._create_gmail_service(self.searchDatabase("ThreadID", thread_id)[0]["GmailToken"])
                        output = str(self._callFunctionByName(function_name, arguments))
                        outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": output
                        })
                        self.service = None
                self._submitRunToolOutput(thread_id, run.id, outputs)
            elif run.status == "failed" or run.status == "cancelled":
                print("Error occurred while running assistant.")
                return

            time.sleep(1)
            run = self._retrieveRun(thread_id, run.id)
            
        # Retrieve assistant response
        response = self.openai_client.beta.threads.messages.list(thread_id).data[0].content[0].text.value
        return response

    def _createMessage(self, thread_id, message, file_ids = []):
        thread_message = self.openai_client.beta.threads.messages.create(
            thread_id,
            role = "user",
            content = message,
            file_ids = file_ids
        )
        return thread_message
    
    def _createThread(self):
        thread = self.openai_client.beta.threads.create()
        return thread.id

    
    def _createRun(self, thread_id):
        run = self.openai_client.beta.threads.runs.create(
            thread_id = thread_id,
            assistant_id = self.id
        )
        return run
    
    def _retrieveRun(self, thread_id, run_id):
        run = self.openai_client.beta.threads.runs.retrieve(
            thread_id = thread_id,
            run_id = run_id
        )
        return run
    
    def _submitRunToolOutput(self, thread_id, run_id, outputs):
        run = self.openai_client.beta.threads.runs.submit_tool_outputs(
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

    def newUserOnboard(self, sender):
        # Create new thread
        thread_id = self._createThread()
        user_id = str(uuid.uuid4())

        # Add user to database
        self.register(sender, user_id, sender, thread_id)

        # Send welcome login message
        self.sendMessage(sender, "Welcome to Persona Corps! Please register your email to continue. https://personacorps.com/login/" + user_id)

    def processNewMessage(self, sender, message):
        print(f"New message from {sender}: {message}")
        result = self.searchDatabase("PhoneNumber", sender)
        
        # if no numer is found, call newUserOnboard
        # if a number is found but no email is found do nothing
        # if a number and email is found, call chat

        if len(result) == 0 or ("PhoneNumber" not in result[0]):
            self.newUserOnboard(sender)
        elif "PhoneNumber" in result[0] and "Email" not in result[0]:
            pass
        elif "PhoneNumber" in result[0] and "Email" in result[0] and "ThreadID" in result[0]:
            thread_id = result[0]["ThreadID"]
            response = self.chat(thread_id, message)
            self.sendMessage(sender, response)
    
if __name__ == "__main__":
    # Create an assistant
    name = "Eve, Personal Assistant"
    instructions = "You are a helpful assistant. You are a young woman named Eve. You conduct yourself very professionally, which you must because you deal with clients personal information, but can sometimes let your guard down depending on the client."
    description = "Eve is a personal assistant that helps you with your daily tasks."
    model = "gpt-4-1106-preview"
    tools = []
    with open('assistant-tools.json') as f:
        tools = json.load(f)
    Assistant(name, description, instructions, model, tools)
    print(Assistant.id)