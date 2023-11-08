import os
from dotenv import load_dotenv
from datetime import datetime
from threading import Thread
from whatsapp_api_client_python import API
import azure_speech_api

load_dotenv()
greenAPI = API.GreenApi(
    os.getenv('GREENAPI_ID'), os.getenv('GREENAPI_TOKEN')
)


def main():
    # receiver = os.getenv('MAX_NUM')
    receiver = os.getenv('JEE_NUM')
    receivingNotificationsThread = Thread(target=receivingNotificationsTask)
    receivingNotificationsThread.daemon = True
    receivingNotificationsThread.start()

    while True:
        message = input(f"Reply @{receiver} if you want:\n")
        filePath = azure_speech_api.synthesize_audio_from_text(message)
        if filePath:
            fileName = filePath[filePath.rfind('/')+1:]
            greenAPI.sending.sendFileByUpload(
                receiver,
                filePath,
                fileName,
            )
        else:
            greenAPI.sending.sendMessage(receiver, "Human: "+message)
    

def receivingNotificationsTask() -> None:
    greenAPI.webhooks.startReceivingNotifications(handler)


def handler(type_webhook: str, body: dict) -> None:
    print(body)
    
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

    # data = dumps(body, ensure_ascii=False, indent=4)
    # print(data)

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
        downloadUrl = messageData["downloadUrl"]
        fileName = messageData["fileName"]
        caption = messageData["caption"]

        print(f'{senderName}: "{caption}"', end='\n\n')
        greenAPI.sending.sendFileByUrl(
            sender,
            downloadUrl,
            fileName,
            "Robot: "+ caption,
        )
    elif typeMessage == "audioMessage":
        messageData = body["messageData"]["fileMessageData"]
        downloadUrl = messageData["downloadUrl"]
        messageText = azure_speech_api.recognize_text_from_audio(downloadUrl)
        if messageText:
            greenAPI.sending.sendMessage(sender, typeMessage+": "+messageText)

    # else:


if __name__ == '__main__':
    main()