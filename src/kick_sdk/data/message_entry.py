import json


class MessageEntry:
    def __init__(self, data: str):
        loaded_json = json.loads(data)
        data = json.loads(loaded_json['data'])

        self.id = data['message']['id']
        self.chatroom_id = data['message']['chatroom_id']
        self.message = data['message']['message']
        self.user_id = data['user']['id']
        self.username = data['user']['username']
        self.type = data['message']['type']
        self.role = data['user']['role']
