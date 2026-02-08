"""AutoMuse CLI -- the Muse in your terminal."""

from __future__ import annotations

import sys

from automuse.muse.engine import Muse


BANNER = r"""
    _         _        __  __
   / \  _   _| |_ ___ |  \/  |_   _ ___  ___
  / _ \| | | | __/ _ \| |\/| | | | / __|/ _ \
 / ___ \ |_| | || (_) | |  | | |_| \__ \  __/
/_/   \_\__,_|\__\___/|_|  |_|\__,_|___/\___|

Layer 1: The Conversation
Type 'help' for commands, or just tell me what you want to make.
"""


def main() -> None:
    print(BANNER)
    muse = Muse()
    print(f"  Session: {muse.key.name} | {muse.tempo} | {muse.time_signature}\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSee you next session.")
            break

        if not user_input:
            continue

        response = muse.respond(user_input)
        if response == "SESSION_END":
            print("Muse: See you next session.")
            break

        print(f"\nMuse: {response}\n")


if __name__ == "__main__":
    main()
