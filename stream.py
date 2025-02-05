import argparse

from now_playing import show_now_playing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=False, action="store_true", help="Show intro.")
    parser.add_argument("--break", required=False, action="store_true", help="Show a break message.")
    parser.add_argument("--now-playing", required=False, action="store_true", help="What is playing right now.")
    args = parser.parse_args()

    if args.now_playing:
        show_now_playing()


if __name__ == '__main__':
    main()
