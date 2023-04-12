import kick_sdk as kickSDK
import util.logger as logger

if __name__ == "__main__":
    ## Authorize with Kick API before using any of the functions
    kick = kickSDK.KickSDK("complisorcu1983@yahoo.com", "37d70e53dce71f2065e9e1181f1bf077|=L|[|{ U@$XSL")

    logger.success("Logged in as " + kick.user.username + "!")

    TARGET_CHANNEL = "devvince"

    ## Retrieve the channel ID of a channel
    channel_id = kick.get_channel_id(TARGET_CHANNEL)

    if channel_id == -1:
        logger.error("Failed to retrieve channel ID!")
        exit(1)
        
    ## Get the chatroom ID of a channel
    chatroom_id = kick.get_chatroom_id(TARGET_CHANNEL)

    if chatroom_id == -1:
        logger.error("Failed to retrieve chatroom ID!")
        exit(1)

    ## Send a message to a channel
    if kick.send_message(chatroom_id, "Hello, world!"):
        logger.success("Successfully sent message!")
    else:
        logger.error("Failed to send message!")