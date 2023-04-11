from time import sleep
import tls_client
import util.logger as logger

from urllib.parse import unquote

from data.authenticated_user import User

default_headers = {
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

auth_headers = {
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
        request = self.session.get("https://kick.com", headers=default_headers)
        csrf_token = unquote(request.cookies.get('XSRF-TOKEN'))

        auth_headers["X-XSRF-TOKEN"] = csrf_token

        self.session.headers["Authorization"] = f"Bearer {unquote(request.cookies['XSRF-TOKEN'])}"
        self.session.headers["X-XSRF-TOKEN"] = csrf_token

        request = self.session.get(
            "https://kick.com/kick-token-provider", headers=auth_headers)
        tokens = request.json()

        sleep(2)

        auth_headers["authorization"] = f"Bearer {unquote(request.cookies['XSRF-TOKEN'])}"

        login_json = {"email": username, "password": password, tokens["nameFieldName"]: "",
                      "_kick_token_valid_from": tokens["encryptedValidFrom"]}

        request = self.session.post("https://kick.com/login",
                                    json=login_json, headers=auth_headers)

        if request.status_code != 204:
            return None

        request = self.session.get(
            "https://kick.com/api/v1/user", headers=auth_headers)
        return User(request.json())

    def send_message(self, chatroom_id: int, message: str) -> bool:
        request = self.session.get("https://kick.com/", headers=auth_headers)
        csrf_token = unquote(request.cookies.get('XSRF-TOKEN'))

        auth_headers["Authorization"] = f"Bearer {unquote(request.cookies['XSRF-TOKEN'])}"
        auth_headers["X-XSRF-TOKEN"] = csrf_token

        request = self.session.post("https://kick.com/api/v1/chat-messages", headers=auth_headers,
                                    json={"chatroom_id": chatroom_id, "message": message})

        if request.status_code != 200:
            return False
        return True

    def get_chatroom_id(self, channel: str) -> int:
        request = self.session.get(f"https://kick.com/api/v1/channels/{channel}",
                                   headers=default_headers)
        if request.status_code != 200:
            return -1
        return request.json()['chatroom']['id']

    def get_channel_id(self, channel: str) -> int:
        request = self.session.get(f"https://kick.com/api/v1/channels/{channel}",
                              headers=default_headers)

        if request.status_code != 200:
            return -1
        return request.json()['id']
