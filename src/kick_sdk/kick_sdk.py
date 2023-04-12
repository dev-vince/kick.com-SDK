import json
import ssl
from time import sleep
import tls_client
import websocket

import util.logger as logger

from urllib.parse import unquote

from data.authenticated_user import User
from src.kick_sdk.data.message_entry import MessageEntry

DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": "",
    "Connection": "keep-alive",
    "Host": "kick.com",
    "sec-ch-ua": '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "X-XSRF-TOKEN": ""
}

AUTH_HEADERS = {
    'authority': 'kick.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US',
    'authorization': 'Bearer',
    'content-type': 'application/json',
    'origin': 'https://kick.com',
    'referer': 'https://kick.com/',
    'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'x-socket-id': '22345.5177199',
    'X-XSRF-TOKEN': "",
}


class KickSDK:
    def __init__(self, username: str, password: str):
        self.session = tls_client.Session(client_identifier="chrome110",
                                          random_tls_extension_order=True)
        self.user = self.login(username, password)
        if self.user is None:
            logger.error("Failed to login!")
            exit(1)

    def login(self, username: str, password: str) -> User:
        request = self.session.get("https://kick.com", headers=DEFAULT_HEADERS)
        csrf_token = unquote(request.cookies.get('XSRF-TOKEN'))

        AUTH_HEADERS["X-XSRF-TOKEN"] = csrf_token

        self.session.headers["Authorization"] = f"Bearer {unquote(request.cookies['XSRF-TOKEN'])}"
        self.session.headers["X-XSRF-TOKEN"] = csrf_token

        request = self.session.get(
            "https://kick.com/kick-token-provider", headers=AUTH_HEADERS)
        tokens = request.json()

        sleep(2)

        AUTH_HEADERS["authorization"] = f"Bearer {unquote(request.cookies['XSRF-TOKEN'])}"

        login_json = {"email": username, "password": password, tokens["nameFieldName"]: "",
                      "_kick_token_valid_from": tokens["encryptedValidFrom"]}

        request = self.session.post("https://kick.com/login",
                                    json=login_json, headers=AUTH_HEADERS)

        if request.status_code != 204:
            return None

        request = self.session.get(
            "https://kick.com/api/v1/user", headers=AUTH_HEADERS)
        return User(request.json())

    def send_message(self, chatroom_id: int, message: str) -> bool:
        request = self.session.get("https://kick.com/", headers=AUTH_HEADERS)
        csrf_token = unquote(request.cookies.get('XSRF-TOKEN'))

        AUTH_HEADERS["Authorization"] = f"Bearer {unquote(request.cookies['XSRF-TOKEN'])}"
        AUTH_HEADERS["X-XSRF-TOKEN"] = csrf_token

        request = self.session.post("https://kick.com/api/v1/chat-messages", headers=AUTH_HEADERS,
                                    json={"chatroom_id": chatroom_id, "message": message})

        if request.status_code != 200:
            return False
        return True

    def send_reply_message(self, chatroom_id: int, message: str, reply_message: MessageEntry) -> bool:
        request = self.session.get("https://kick.com/", headers=AUTH_HEADERS)
        csrf_token = unquote(request.cookies.get('XSRF-TOKEN'))

        AUTH_HEADERS["Authorization"] = f"Bearer {unquote(request.cookies['XSRF-TOKEN'])}"
        AUTH_HEADERS["X-XSRF-TOKEN"] = csrf_token

        request = self.session.post("https://kick.com/api/v1/chat-messages", headers=AUTH_HEADERS,
                                    json={"chatroom_id": chatroom_id, "message": message, "replied_to": {
                                        "id": reply_message.id,
                                        "message": reply_message.message,
                                        "username": reply_message.username
                                    }})

        if request.status_code != 200:
            return False
        return True

    def get_chatroom_id(self, channel: str) -> int:
        request = self.session.get(f"https://kick.com/api/v1/channels/{channel}",
                                   headers=DEFAULT_HEADERS)
        if request.status_code != 200:
            return -1
        return request.json()['chatroom']['id']

    def get_channel_id(self, channel: str) -> int:
        request = self.session.get(f"https://kick.com/api/v1/channels/{channel}",
                                   headers=DEFAULT_HEADERS)

        if request.status_code != 200:
            return -1
        return request.json()['id']

    def follow_channel(self, channel_id: int) -> bool:
        request = self.session.post(f"https://kick.com/api/v1/channels/{channel_id}/follow",
                                    headers=AUTH_HEADERS)
        if request.status_code != 201:
            return False
        return True

    def unfollow_channel(self, channel_id: int) -> bool:
        request = self.session.post(f"https://kick.com/api/v1/channels/{channel_id}/follow",
                                      headers=AUTH_HEADERS)
        if request.status_code != 200:
            return False
        return True

    def delete_message(self, message: MessageEntry):
        body = {"chatroom_id": str(message.chatroom_id), "message_id": message.id, "deleted": True, "deleted_by": self.user.id}

        request = self.session.post(f"https://kick.com/api/v1/chat-messages/{message.id}",
                                      headers=AUTH_HEADERS, json=body)
        if request.status_code != 200:
            return False
        return True

    def connect_to_chat(self, channel_id: int, chatroom_id: int) -> websocket.WebSocket:
        ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        ws.connect("wss://ws-us2.pusher.com/app/eb1d5f283081a78b932c?protocol=7&client=js&version=7.4.0&flash=false")

        sleep(0.5)

        ws.send(
            json.dumps({"event": "pusher:subscribe", "data": {"auth": "", "channel": "channel." + str(channel_id)}}))
        ws.send(
            json.dumps({"event": "pusher:subscribe", "data": {"auth": "", "channel": "chatrooms." + str(chatroom_id)}}))
        return ws
