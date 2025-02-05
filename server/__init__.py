import requests
import base64

from dotenv import dotenv_values
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from spotify_access_token import Token


class Server(BaseHTTPRequestHandler):
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

        access_token = Token(
            api_token_response["access_token"],
            api_token_response["refresh_token"],
            api_token_response["token_type"],
            api_token_response["expires_in"]
        )

        self.server.access_token = access_token

    def log_message(self, format, *args):
        return
