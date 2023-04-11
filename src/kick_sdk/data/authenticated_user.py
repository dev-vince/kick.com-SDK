class User:
    def __init__ (self, json: str):
        self.username = json['username']
        self.id = json['id']
        self.email = json['email']
        self.channel_id = json['streamer_channel']['id']
        self.is_banned = json['streamer_channel']['is_banned']