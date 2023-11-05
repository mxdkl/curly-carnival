import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime
from threading import Thread
from whatsapp_api_client_python import API

load_dotenv()
greenAPI = API.GreenApi(
    os.getenv('GREENAPI_ID'), os.getenv('GREENAPI_TOKEN')
)


def main():
    receiver = os.getenv('MAX_NUM')
    # receiver = os.getenv('JEE_NUM')
    receivingNotificationsThread = Thread(target=receivingNotificationsTask)
    receivingNotificationsThread.daemon = True
    receivingNotificationsThread.start()

    while True:
        message = input(f"Reply @{receiver} if you want:\n")
        url = getAudioFromText(message)
        if url:
            fileName = url[url.rfind('/')+1:]
            greenAPI.sending.sendFileByUrl(
                receiver,
                url,
                fileName,
            )
        else:
            greenAPI.sending.sendMessage(receiver, "Human: "+message)
    

def receivingNotificationsTask() -> None:
    greenAPI.webhooks.startReceivingNotifications(handler)


def handler(type_webhook: str, body: dict) -> None:
    if type_webhook == "incomingMessageReceived":
        incoming_message_received(body)
"""
    elif type_webhook == "outgoingMessageReceived":
        outgoing_message_received(body)
    elif type_webhook == "outgoingAPIMessageReceived":
        outgoing_api_message_received(body)
    elif type_webhook == "outgoingMessageStatus":
        outgoing_message_status(body)
    elif type_webhook == "stateInstanceChanged":
        state_instance_changed(body)
    elif type_webhook == "deviceInfo":
        device_info(body)
    elif type_webhook == "incomingCall":
        incoming_call(body)
    elif type_webhook == "statusInstanceChanged":
        status_instance_changed(body) """

def get_notification_time(timestamp: int) -> str:
    return str(datetime.fromtimestamp(timestamp))

def incoming_message_received(body: dict) -> None:
    timestamp = body["timestamp"]
    time = get_notification_time(timestamp)

    data = dumps(body, ensure_ascii=False, indent=4)
    print(data)

    sender = body["senderData"]["sender"]
    senderName = body["senderData"]["senderName"]
    typeMessage = body["messageData"]["typeMessage"]
    print(f'New incoming message at {time} from {senderName} with {typeMessage}')

    if typeMessage == "textMessage" or typeMessage == "extendedTextMessage":
        if typeMessage == "textMessage":
            messageData = body["messageData"]["textMessageData"]
            textMessage = messageData["textMessage"]
        else:
            messageData = body["messageData"]["extendedTextMessageData"]
            textMessage = messageData["text"]
        print(f'{senderName}: "{textMessage}"', end='\n\n')
        greenAPI.sending.sendMessage(sender, "Robot: "+textMessage)

    elif typeMessage == "imageMessage" or typeMessage == "videoMessage":
        messageData = body["messageData"]["fileMessageData"]
        imageUrl = messageData["downloadUrl"]
        fileName = messageData["fileName"]
        caption = messageData["caption"]

        print(f'{senderName}: "{caption}"', end='\n\n')
        greenAPI.sending.sendFileByUrl(
            sender,
            imageUrl,
            fileName,
            "Robot: "+ caption
        )

    elif typeMessage == "audioMessage":
        messageData = body["messageData"]["fileMessageData"]
        imageUrl = messageData["downloadUrl"]
        fileName = messageData["fileName"]

        print(f'{senderName}: "{caption}"', end='\n\n')
        greenAPI.sending.sendFileByUpload(
            sender,
            "data/green-api-logo_2.png",
            "green-api-logo_2.png",
        )

    # else:
def getAudioFromText(message: str) -> str:
    if message:
        url = "https://api.play.ht/api/v2/tts"
        payload = {
            "text": message,
            "voice": "s3://mockingbird-prod/ayla_vo_expressive_16095e08-b9e8-429b-947c-47a75e41053b/voices/speaker/manifest.json",
            "output_format": "mp3",
            "voice_engine": "PlayHT2.0"
        }
        headers = {
            "accept": "text/event-stream",
            "content-type": "application/json",
            "AUTHORIZATION": os.getenv('PLAYHT_TOKEN'),
            "X-USER-ID": os.getenv('PLAYHT_ID')
        }
        # print(headers)
        response = requests.post(url, json=payload, headers=headers)

        # print(response.text)
        if response.text.rfind("completed"):
            data=json.loads(response.text[response.text.rfind('{'):])
            return(data["url"])


if __name__ == '__main__':
    main()