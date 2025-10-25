import argparse
import random
import time
import os
import platform
from typing import List, Sequence

STRINGS: List[int] = [1, 2, 3, 4, 5, 6]
NOTES: List[str] = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NOTES_NATURAL: List[str] = ["C", "D", "E", "F", "G", "A", "B"]

DEFAULT_TIME = 10  # seconds


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Guitar fingerboard trainer")
    p.add_argument(
        "--auto",
        nargs="?",
        type=int,
        const=DEFAULT_TIME,
        help="run automatically every N seconds",
    )
    p.add_argument(
        "--accidentals",
        action="store_true",
        help="include accidentals (sharps) in the note pool",
    )
    p.add_argument("--string", type=int, help="practice a specific string [1-6]")
    p.add_argument("--note", type=str, help="practice a specific note (e.g., C, F#)")

    return p.parse_args()


def clear() -> None:
    os.system("cls" if platform.system() == "Windows" else "clear")


def build_note_pool(args: argparse.Namespace) -> Sequence[str]:
    if args.note:
        return [args.note]
    return NOTES if args.accidentals else NOTES_NATURAL


def choose_prompt(args: argparse.Namespace) -> tuple[int, str]:
    s = args.string or random.choice(STRINGS)
    note_pool = build_note_pool(args)
    n = random.choice(note_pool)
    return s, n


def run_auto(args: argparse.Namespace) -> None:
    print("Ctrl + C to quit.")
    time.sleep(1.0)
    buffer = max(0, args.auto)
    # keep steady cadence using monotonic time
    next_tick = time.monotonic()
    while True:
        clear()
        s, n = choose_prompt(args)
        print(f"String: {s}, Note: {n}")
        next_tick += buffer
        time.sleep(max(0.0, next_tick - time.monotonic()))


def run_manual(args: argparse.Namespace) -> None:
    print("Press Enter to continue, or type 'q' to quit.")
    while True:
        clear()
        s, n = choose_prompt(args)
        print(f"String: {s}, Note: {n}")
        choice = input("> ").strip().lower()
        if choice in {"q", "quit", "exit"}:
            print("Stopped.")
            return


def main() -> None:
    args = parse_args()

    try:
        if args.auto:
            run_auto(args)
        else:
            run_manual(args)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
