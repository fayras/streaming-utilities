import asyncio
import sqlite3

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator

from config import config
from db import is_current_version

import twitch_server.webserver
import twitch_server.bot


async def get_twitch_api():
    # set up twitch api instance and add user authentication with some scopes
    twitch = await Twitch(config.twitch_app_id, config.twitch_app_secret)
    auth = UserAuthenticator(twitch, config.twitch_user_scopes,
                             url="http://localhost:8990",
                             port=8990)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, config.twitch_user_scopes,
                                         refresh_token)

    return twitch


async def run_tasks(twitch, webserver_app, websocket_manager):
    await asyncio.gather(
        webserver.run(webserver_app),
        bot.run(twitch, websocket_manager)
    )


def start_twitch_server():
    con = sqlite3.connect(config.database_path)
    if not is_current_version(con):
        raise Exception("Database version is out of date.")

    loop = asyncio.get_event_loop()
    twitch_app = loop.run_until_complete(get_twitch_api())
    webserver_app, websocket_manager = webserver.setup(twitch_app)

    try:
        asyncio.run(run_tasks(twitch_app, webserver_app, websocket_manager))
    except KeyboardInterrupt:
        pass
