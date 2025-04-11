from dotenv import dotenv_values
from twitchAPI.type import AuthScope


class Config:
    def __init__(self):
        print("config constructor")
        env_value = dotenv_values(".env")

        self.spotify_client_id = env_value["SPOTIFY_CLIENT_ID"]
        self.spotify_client_secret = env_value["SPOTIFY_CLIENT_SECRET"]
        self.spotify_redirect_uri = env_value["SPOTIFY_REDIRECT_URI"]

        self.twitch_app_id = env_value["TWITCH_APP_ID"]
        self.twitch_app_secret = env_value["TWITCH_APP_SECRET"]
        self.twitch_target_channel = env_value["TWITCH_CHANNEL"]
        self.twitch_redirect_uri = env_value["TWITCH_REDIRECT_URI"]
        self.twitch_user_scopes = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

        self.discord_invite_link = env_value["DISCORD_INVITE_LINK"]

        self.database_path = env_value["DATABASE_PATH"]


config = Config()
