import os
import azure_speech_api
from dotenv import load_dotenv
from whatsapp_api_client_python import API

load_dotenv()
greenAPI = API.GreenApi(
    os.getenv('GREENAPI_ID'), os.getenv('GREENAPI_TOKEN')
)

class GreenApiWrapper:
    def __init__(self):
        self.chat_history = {}

    def sendMessage(self, receiver: str, message: str, attachment = None) -> None:
        if receiver not in self.chat_history:
            self.chat_history[receiver] = []
        self.chat_history[receiver].append(message)
        if attachment:
            self._sendFileByUpload(receiver, attachment, attachment, message)
        else:
            greenAPI.sending.sendMessage(receiver, message)

    def _sendFileByUpload(self, receiver: str, file_path: str, file_name: str, caption: str) -> None:
        if receiver not in self.chat_history:
            self.chat_history[receiver] = []
        self.chat_history[receiver].append(caption)
        greenAPI.sending.sendFileByUpload(receiver, file_path, file_name, caption)

    def receivingMessage(self) -> None:
        greenAPI.webhooks.startReceivingNotifications(self._handler)

    def _handler(self, type_webhook: str, body: dict) -> None:
        if type_webhook == "incomingMessageReceived":
            self._incoming_message_received(body)

    def _incoming_message_received(body: dict) -> None:
        sender = body["senderData"]["sender"]
        senderName = body["senderData"]["senderName"]
        typeMessage = body["messageData"]["typeMessage"]
        print(f'New incoming message from {senderName} with {typeMessage}')

        if typeMessage == "textMessage" or typeMessage == "extendedTextMessage":
            if typeMessage == "textMessage":
                messageData = body["messageData"]["textMessageData"]
                textMessage = messageData["textMessage"]
            else:
                messageData = body["messageData"]["extendedTextMessageData"]
                textMessage = messageData["text"]
            print(f'{senderName}: "{textMessage}"', end='\n\n')

        elif typeMessage == "imageMessage" or typeMessage == "videoMessage":
            messageData = body["messageData"]["fileMessageData"]
            downloadUrl = messageData["downloadUrl"]
            fileName = messageData["fileName"]
            caption = messageData["caption"]
            print(f'{senderName}: "{caption}"', end='\n\n')

        elif typeMessage == "audioMessage":
            messageData = body["messageData"]["fileMessageData"]
            downloadUrl = messageData["downloadUrl"]
            fileName = messageData["fileName"]
            caption = messageData["caption"]

            messageText = azure_speech_api.recognize_text_from_audio(downloadUrl)
            if messageText:
                print(f'{senderName}: "{messageText}"(recognized)', end='\n\n')
            else:
                print(f'{senderName}: "{caption}"', end='\n\n')

