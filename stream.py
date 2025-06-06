import argparse

from now_playing import show_now_playing
from current_task import show_current_task
from twitch_server import start_twitch_server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=False, action="store_true",
                        help="Show intro.")
    parser.add_argument("--break", required=False, action="store_true",
                        help="Show a break message.")
    parser.add_argument("--now-playing", required=False, action="store_true",
                        help="What is playing right now.")
    parser.add_argument("--current-task", required=False, action="store_true",
                        help="What is the current task right now.")
    parser.add_argument("--twitch-server", required=False, action="store_true",
                        help="Start a server which listens for Twitch Events.")

    args = parser.parse_args()

    if args.now_playing:
        show_now_playing()

    if args.current_task:
        show_current_task()

    if args.twitch_server:
        start_twitch_server()


if __name__ == '__main__':
    main()
