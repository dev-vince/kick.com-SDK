import json
import threading
import time

import kick_sdk as kickSDK
import util.logger as logger
from src.kick_sdk.data import message_entry

BLACKLISTED_WORDS = ["fuck", "bitch", "shit", "ass", "dick"]


def channel_listener(channel: str) -> None:
    channel_id = kick.get_channel_id(channel)
    chatroom_id = kick.get_chatroom_id(channel)
    websocket = kick.connect_to_chat(channel_id, chatroom_id)

    while True:
        message = websocket.recv()
        data = json.loads(message)
        event = data["event"]
        if event == "App\Events\ChatMessageSentEvent":
            msg = message_entry.MessageEntry(message)

            split = msg.message.split(" ")
            for word in split:
                for blacklisted in BLACKLISTED_WORDS:
                    if blacklisted.lower() in word.lower():
                        time.sleep(0.2)
                        if not kick.delete_message(msg):
                            if not kick.delete_message(msg):
                                logger.warning(f"Message {msg.message} could not be deleted!")

                        kick.send_message(chatroom_id, f"@{msg.username}, do not swear in the chat!")
                        break

if __name__ == "__main__":
    global kick
    kick = kickSDK.KickSDK("username", "password")

    logger.success("Logged in as " + kick.user.username + "!")

    while True:
        target_channel = input("Enter the channel you want to listen to: ")
        thread = threading.Thread(target=channel_listener, args=(target_channel,))
        thread.start()
