import os
import json
import requests
import azureAPI
from datetime import datetime
from threading import Thread
from dotenv import load_dotenv
from whatsapp_api_client_python import API

class GreenApiWrapper:
    def __init__(self):
        load_dotenv()
        self.greenAPI = API.GreenApi(
            os.getenv('GREENAPI_ID'), os.getenv('GREENAPI_TOKEN')
        )
        self.recipient = None
        self.chat_history = {}

    def sendTextMessage(self, receiver: str, message: str, attachment = None) -> requests.Response:
        if attachment:
            self._sendFileByUpload(receiver, attachment, attachment)
        else:
            self._storeChatHistory(receiver, message)
            response = self.greenAPI.sending.sendTextMessage(receiver, message)
            return response

    def sendVoiceMessage(self, receiver: str, message: str):
        if message:
            
            url = "https://api.play.ht/api/v2/tts"
            payload = {
                "text": message,
                "voice": "s3://mockingbird-prod/ayla_vo_meditation_d11dd9da-b5f1-4709-95a6-e6d5dc77614a/voices/speaker/manifest.json",
                "output_format": "mp3",
                "voice_engine": "PlayHT2.0"
            }
            headers = {
                "accept": "text/event-stream",
                "content-type": "application/json",
                "AUTHORIZATION": os.getenv('PLAYHT_TOKEN'),
                "X-USER-ID": os.getenv('PLAYHT_ID')
            }
            audioResponse = requests.post(url, json=payload, headers=headers)
            if audioResponse.text.rfind("completed"):
                data=json.loads(audioResponse.text[audioResponse.text.rfind('{'):])
                url=data["url"]
                # print(url)
                fileName = url[url.rfind('/')+1:]
                self._sendFileByUrl(receiver, url, fileName)

    def _storeChatHistory(self, receiver: str, content: str):
        if receiver not in self.chat_history:
            self.chat_history[receiver] = []
        self.chat_history[receiver].append(content)

    def _sendFileByUpload(self, receiver: str, file_path: str, file_name: str, caption: str)-> requests.Response:
        self._storeChatHistory(self, receiver, caption)
        response = self.greenAPI.sending.sendFileByUpload(receiver, file_path, file_name, caption)
        return response

    def _sendFileByUrl(self, receiver: str, url: str, file_name: str, caption: str = None) -> requests.Response:
        self._storeChatHistory(self, receiver, caption)
        response = self.greenAPI.sending.sendFileByUrl(receiver, url, file_name, caption)
        return response

    def receivingMessage(self) -> None:
        receivingNotificationsThread = Thread(target = self._receivingNotificationsTask)
        receivingNotificationsThread.daemon = True
        receivingNotificationsThread.start()

    def _notifyReceivedMessage(self, data):
        self.recipient.getNewMessage(data)

    def _receivingNotificationsTask(self):
        self.greenAPI.webhooks.startReceivingNotifications(self._handler)
        print("GreenAPI is receiving messages in a daemon thread...")

    def _handler(self, type_webhook: str, body: dict) -> None:
        if type_webhook == "incomingMessageReceived":
            self._incoming_message_received(body)

    def _get_notification_time(timestamp: int) -> str:
        return str(datetime.fromtimestamp(timestamp))

    def _incoming_message_received(self, body: dict) -> None:
        sender = body["senderData"]["sender"]
        senderName = body["senderData"]["senderName"]
        typeMessage = body["messageData"]["typeMessage"]
        print(f'New incoming message from {senderName} with {typeMessage}\n')

        self._notifyReceivedMessage(body)

"""         if typeMessage == "textMessage" or typeMessage == "extendedTextMessage":
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

            messageText = azureAPI.recognize_text_from_audio(downloadUrl)
            if messageText:
                print(f'{senderName}: "{messageText}"(recognized)', end='\n\n')
            else:
                print(f'{senderName}: "{caption}"', end='\n\n') """
        

