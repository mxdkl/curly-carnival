import os
from dotenv import load_dotenv
from openai import OpenAI


class OpenAIWrapper:
    def __init__(self):
        load_dotenv()
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.chat_history = []

    def createAssistant(self, name, description, instructions, model, tools, files):
        assistant = self.openai_client.beta.assistants.create(
            name=name,
            instructions=instructions,
            description=description,
            model=model,
            tools=tools,
        )
        return assistant.id

    def generateImage(self, prompt):
        response = self.openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        return response['data'][0]['url']

    def _uploadFiles(files):
        file_ids = []
        for file in files:
            pass
        return file_ids
