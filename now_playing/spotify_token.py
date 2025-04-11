import datetime
import webbrowser
import requests
import base64

from urllib.parse import urlencode
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from config import config


class SpotifyTokenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(
            b"""
            <html>
            <head>
                <title>Spotify Token</title>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            </head>
            <body style="text-align:center; padding-top: 5em; color: #999">
                <h1>Spotify Code Authorization successful</h1>
                <h2>You can now close this window</h2>
            </body>
            </html>
            """
        )

        access_code = parse_qs(urlparse(self.path).query)["code"]
        self.server.spotify_access_code = access_code

    def log_message(self, _, *args):
        return


class SpotifyAuthServer(HTTPServer):
    spotify_access_code = None

    def __init__(self):
        HTTPServer.__init__(self, ("localhost", 8989), SpotifyTokenHandler)


class SpotifyToken:
    def __init__(self, access_token, refresh_token, token_type, expires_in):
        self.token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.expires_at = datetime.datetime.now() + datetime.timedelta(
            seconds=expires_in)

    @staticmethod
    def get():
        params = urlencode({
            "response_type": "code",
            "scope": "user-read-currently-playing user-modify-playback-state playlist-modify-public",
            "redirect_uri": config.spotify_redirect_uri,
            "client_id": config.spotify_client_id,
        })

        with SpotifyAuthServer() as server:
            webbrowser.open("https://accounts.spotify.com/authorize?" + params)
            server.handle_request()
            access_code = server.spotify_access_code

        return SpotifyToken.request_token_with_code(access_code)

    @staticmethod
    def get_headers():
        id_secret_string = f"{config.spotify_client_id}:{config.spotify_client_secret}"
        return {
            "Authorization": "Basic " + base64.b64encode(
                id_secret_string.encode('ascii')).decode(),
            "Content-Type": "application/x-www-form-urlencoded"
        }

    @staticmethod
    def request_token_with_code(code):
        headers = SpotifyToken.get_headers()
        api_token_params = {
            "grant_type": "authorization_code",
            "redirect_uri": config.spotify_redirect_uri,
            "code": code
        }

        code, api_token_response = SpotifyToken.get_token_from_api(
            api_token_params,
            headers
        )

        return SpotifyToken(
            api_token_response["access_token"],
            api_token_response["refresh_token"],
            api_token_response["token_type"],
            api_token_response["expires_in"]
        )

    @staticmethod
    def get_token_from_api(api_token_params, headers):
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data=api_token_params,
            headers=headers
        )

        return response.status_code, response.json()

    def get_from_cache(self):
        pass

    def is_valid(self):
        return datetime.datetime.now() >= self.expires_at

    def refresh(self):
        headers = SpotifyToken.get_headers()
        api_token_params = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }

        code, api_token_response = SpotifyToken.get_token_from_api(
            api_token_params,
            headers
        )

        if code != 200:
            raise Exception("Could not refresh token")

        self.token = api_token_response["access_token"]
        self.refresh_token = (
            api_token_response["refresh_token"]
            if "refresh_token" in api_token_response
            else self.refresh_token
        )
        self.token_type = api_token_response["token_type"]
        self.expires_in = api_token_response["expires_in"]
        self.expires_at = datetime.datetime.now() + datetime.timedelta(
            seconds=self.expires_in)
