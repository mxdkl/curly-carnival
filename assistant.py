import os
import time
import json
from dotenv import load_dotenv
from openaiAPI import OpenAIWrapper
from gmailAPI import GmailWrapper


class Assistant(OpenAIWrapper, GmailWrapper):
    def __init__(self, id, user):
        super().__init__()
        GmailWrapper.__init__(self)

        self.id = id
        self.user = user
        self.threads = self.client.beta.threads.create()

    def chat(self, message: str, attachments: list = []):
        # Create message
        self._createMessage(message, attachments)

        # Run assistant
        run = self.client.beta.threads.runs.create(
            thread_id = self.threads.id,
            assistant_id = self.id
        )

        # Wait for assistant to finish. This code jank af
        while run.status != "completed":
            if run.status == "requires_action":
                outputs = []
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    if tool_call.type == "function":
                        # Run function called by assistant here
                        arguments = json.loads(tool_call.function.arguments)
                        function_name = tool_call.function.name
                        output = str(self._callFunctionByName(function_name, arguments))
                        outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": output
                        })
                self._submitRunToolOutput(run.id, outputs)

            time.sleep(1)
            run = self._retrieveRun(run.id)
            
        # Retrieve assistant response
        response = self.client.beta.threads.messages.list(self.threads.id).data
        return response

    def _createMessage(self, message, file_ids = []):
        thread_message = self.client.beta.threads.messages.create(
            self.threads.id,
            role = "user",
            content = message,
            file_ids = file_ids
        )
        return thread_message
    
    def _retrieveRun(self, run_id):
        run = self.client.beta.threads.runs.retrieve(
            thread_id = self.threads.id,
            run_id = run_id
        )
        return run
    
    def _submitRunToolOutput(self, run_id, outputs):
        run = self.client.beta.threads.runs.submit_tool_outputs(
            thread_id = self.threads.id,
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
    

if __name__ == "__main__":
    # Create an assistant
    name = "Eve, Personal Assistant"
    instructions = "You are a helpful assistant. You are a young woman named Eve. You conduct yourself very professionally, which you must because you deal with clients personal information, but can sometimes let your guard down depending on the client."
    description = "Eve is a personal assistant that helps you with your daily tasks."
    model = "gpt-4-1106-preview"
    tools = []
    with open('assistant-tools.json') as f:
        tools = json.load(f)

    # Create assistant
    #id = OpenAIWrapper.createAssistant(name=name, description=description, instructions=instructions, model=model, tools=tools, files=None)

    load_dotenv()
    id = os.getenv("ASSISTANT_ID")
    user = "test"
    eve = Assistant(id, user)
    print(eve.chat("send dingjee7@gmail.com an email with the subject test and the message this is a test email"))