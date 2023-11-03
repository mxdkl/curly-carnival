from datetime import datetime
from json import dumps
from threading import Thread
from whatsapp_api_client_python import API


# This whatsapp account is "8615101526507@c.us"
MAX_NUM = "972533642700@c.us"
JEE_NUM = "972549486533@c.us"
greenAPI = API.GreenApi(
    "7103872531", "3e21f47970a74b72a4756729a84a845eb516178db56c4cd6b5"
)


def main():
    receiver = MAX_NUM
    receivingNotificationsThread = Thread(target=receivingNotificationsTask)
    receivingNotificationsThread.daemon = True
    receivingNotificationsThread.start()

    while True:
        message = input(f"Reply @{receiver} if you want:\n")
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

    # data = dumps(body, ensure_ascii=False, indent=4)

    sender = body["senderData"]["sender"]
    senderName = body["senderData"]["senderName"]
    textMessage = body["messageData"]["textMessageData"]["textMessage"]

    print(f'New incoming message at {time} from {senderName} with message: "{textMessage}"', end='\n\n')
    greenAPI.sending.sendMessage(sender, "Robot: "+textMessage)


if __name__ == '__main__':
    main()