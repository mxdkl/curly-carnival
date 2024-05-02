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
            self.id = self.createAssistant(
                name=name, description=description, instructions=instructions, model=model, tools=tools, files=files)


    # Public Methods

    def chat(self, thread_id, message: str, attachments: list = []):
        # Create message
        self._createMessage(thread_id, message, attachments)

        # Run assistant
        run = self._createRun(thread_id)

        # Wait for assistant to finish
        while run.status != "completed":
            if run.status == "failed" or run.status == "cancelled":
                print("Error occurred while running assistant.")
                return
            
            # Run assistant functions
            if run.status == "requires_action":
                outputs = []
                for tool in run.required_action.submit_tool_outputs.tool_calls:
                    if tool.type == "function":
                        arguments = json.loads(tool.function.arguments)
                        arguments["credentials_json"] = self.searchDatabase(
                            "ThreadID", thread_id)[0]["GmailData"]
                        function_name = tool.function.name
                        output = self._callFunctionByName(function_name, arguments)
                        outputs.append({
                            "tool_call_id": tool.id,
                            "output": "True"
                        })

                # Submit assistant function outputs
                self._submitRunToolOutput(thread_id, run.id, outputs)

            time.sleep(1)
            run = self._retrieveRun(thread_id, run.id)
        
        # Retrieve assistant response  
        run = self._retrieveRun(thread_id, run.id)

        # Retrieve assistant response
        response = self.openai_client.beta.threads.messages.list(
            thread_id).data[0].content[0].text.value
        return response
    
    def processNewMessage(self, sender, name, message):
        print(f"New message from {sender}: {message}")
        result = self.searchDatabase("PhoneNumber", sender)

        # if no numer is found, call _newUserOnboard
        # if a number is found but no email is found do nothing
        # if a number and email is found, call chat

        if len(result) == 0 or ("PhoneNumber" not in result[0]):
            self._newUserOnboard(sender, name)
        elif "PhoneNumber" in result[0] and "Email" not in result[0]:
            pass
        elif "PhoneNumber" in result[0] and "Email" in result[0] and "ThreadID" in result[0]:
            thread_id = result[0]["ThreadID"]
            response = self.chat(thread_id, message)
            print(f"Response to {sender}: {response}")
            self.sendMessage(sender, response)
    

    # Private Methods

    def _newUserOnboard(self, sender):
        # Create new thread and user id
        thread_id = self._createThread()
        user_id = str(uuid.uuid4())

        self._createMessage(thread_id=thread_id, message="Hello Eve! My name is " + sender + ".")

        # Add user to database
        self.registerPhoneNumber(user_id, sender, thread_id)

        # Send welcome login message
        self.sendMessage(
            sender, "Welcome to Persona Corps! Please register your email to continue. https://personacorps.com/login/" + user_id)


    def _createMessage(self, thread_id, message, file_ids=[]):
        thread_message = self.openai_client.beta.threads.messages.create(
            thread_id,
            role="user",
            content=message,
            attachments=file_ids
        )
        return thread_message

    def _createThread(self):
        thread = self.openai_client.beta.threads.create()
        return thread.id

    def _createRun(self, thread_id):
        run = self.openai_client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.id
        )
        return run

    def _retrieveRun(self, thread_id, run_id):
        run = self.openai_client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        return run

    def _submitRunToolOutput(self, thread_id, run_id, outputs):
        run = self.openai_client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=outputs
        )
        return run

    def _callFunctionByName(self, function_name, arguments):
        if hasattr(self, function_name) and callable(getattr(self, function_name)):
            func = getattr(self, function_name)
            return func(**arguments)
        else:
            print(f"Function '{function_name}' not found.")
            return "Function not found."