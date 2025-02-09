import datetime
import webbrowser
import requests
import base64

from dotenv import dotenv_values
from urllib.parse import urlencode
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class SpotifyTokenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        env_values = dotenv_values(".env")
        access_code = parse_qs(urlparse(self.path).query)["code"]
        api_token_params = {
            "grant_type": "authorization_code",
            "redirect_uri": env_values["REDIRECT_URI"],
            "code": access_code
        }
        headers = {
            "Authorization":
                "Basic " + base64.b64encode((env_values["CLIENT_ID"] + ":" + env_values["CLIENT_SECRET"])
                                            .encode('ascii')).decode(),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        api_token_response = requests.post(
            "https://accounts.spotify.com/api/token",
            data=api_token_params,
            headers=headers
        ).json()

        token = SpotifyToken()
        token.token = api_token_response["access_token"]
        token.refresh_token = api_token_response["refresh_token"]
        token.token_type = api_token_response["token_type"]
        token.expires_in = api_token_response["expires_in"]
        token.expires_at = datetime.datetime.now() + datetime.timedelta(seconds=token.expires_in)

        self.server.spotify_token = token

    def log_message(self, format, *args):
        return


class SpotifyToken:
    token = None
    refresh_token = None
    token_type = None
    expires_in = None
    expires_at = None

    @staticmethod
    def get():
        env_values = dotenv_values(".env")
        params = urlencode({
            "response_type": "code",
            "scope": "user-read-currently-playing",
            "redirect_uri": env_values["REDIRECT_URI"],
            "client_id": env_values["CLIENT_ID"],
        })

        with HTTPServer(("localhost", 8989), SpotifyTokenHandler) as server:
            webbrowser.open("https://accounts.spotify.com/authorize?" + params)
            server.handle_request()

            return server.spotify_token


    def get_from_cache(self):
        pass


    def check_validity(self):
        pass


    def refresh(self):
        pass


