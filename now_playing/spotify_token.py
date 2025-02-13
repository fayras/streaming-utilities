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

        access_code = parse_qs(urlparse(self.path).query)["code"]
        self.server.spotify_access_code = access_code


    def log_message(self, format, *args):
        return


class SpotifyToken:
    def __init__(self, access_token, refresh_token, token_type, expires_in):
        self.token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.expires_at = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)

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

            access_code = server.spotify_access_code

        return SpotifyToken.request_token_with_code(access_code)


    @staticmethod
    def request_token_with_code(code):
        env_values = dotenv_values(".env")
        id_secret_string = env_values["CLIENT_ID"] + ":" + env_values["CLIENT_SECRET"]
        headers = {
            "Authorization": "Basic " + base64.b64encode(id_secret_string.encode('ascii')).decode(),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        api_token_params = {
            "grant_type": "authorization_code",
            "redirect_uri": env_values["REDIRECT_URI"],
            "code": code
        }
        api_token_response = requests.post(
            "https://accounts.spotify.com/api/token",
            data=api_token_params,
            headers=headers
        ).json()

        return SpotifyToken(
            api_token_response["access_token"],
            api_token_response["refresh_token"],
            api_token_response["token_type"],
            api_token_response["expires_in"]
        )

    def get_from_cache(self):
        pass


    def check_validity(self):
        pass


    def refresh(self):
        pass


