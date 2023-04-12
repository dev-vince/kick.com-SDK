import json

import kick_sdk as kickSDK
import util.logger as logger
from src.kick_sdk.data import message_entry

if __name__ == "__main__":
    # Authorize with Kick API before using any of the functions
    kick = kickSDK.KickSDK("username", "password")

    logger.success("Logged in as " + kick.user.username + "!")

    TARGET_CHANNEL = "devvince"

    # Retrieve the channel ID of a channel
    channel_id = kick.get_channel_id(TARGET_CHANNEL)

    if channel_id == -1:
        logger.error("Failed to retrieve channel ID!")
        exit(1)

    # Get the chatroom ID of a channel
    chatroom_id = kick.get_chatroom_id(TARGET_CHANNEL)

    if chatroom_id == -1:
        logger.error("Failed to retrieve chatroom ID!")
        exit(1)

    # Send a message to a channel
    if kick.send_message(chatroom_id, "Hello, world!"):
        logger.success("Successfully sent message!")
    else:
        logger.error("Failed to send message!")

    websocket = kick.connect_to_chat(channel_id, chatroom_id)

    # Reading in on messages
    while True:
        message = websocket.recv()
        data = json.loads(message)
        event = data["event"]
        if event == "App\Events\ChatMessageSentEvent":
            msg = message_entry.MessageEntry(message)
            logger.info(f"{msg.username}: {msg.message}")

            # Send a reply message to a channel
            if msg.username != kick.user.username:
                if kick.send_reply_message(chatroom_id, "Welcome to the channel!", msg):
                    logger.success("Successfully sent reply message!")

