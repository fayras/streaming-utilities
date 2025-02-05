import datetime


class Token:
    def __init__(self, token, refresh_token, token_type, expires_in):
        self.token = token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.expires_at = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
