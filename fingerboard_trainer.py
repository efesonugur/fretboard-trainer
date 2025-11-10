import argparse
import random
import time
import os
import platform
import sys
from typing import List, Sequence

STRINGS: List[int] = [1, 2, 3, 4, 5, 6]
NOTES: List[str] = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NOTES_NATURAL: List[str] = ["C", "D", "E", "F", "G", "A", "B"]

DEFAULT_TIME = 10  # seconds


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Guitar fretboard trainer")
    p.add_argument(
        "--auto",
        nargs="?",
        type=int,
        metavar="SECONDS",
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

    p.add_argument(
        "--preset",
        nargs="?",
        type=int,
        metavar="SECONDS",
        const=DEFAULT_TIME,
        help="preset mode: cycle through the circle of fifths on each string (must be used alone)",
    )
    
    args = p.parse_args()

    if args.preset is not None:
        conflicting_flags = {"--auto", "--accidentals", "--string", "--note"}
        used_conflicts = [tok for tok in sys.argv[1:] if tok in conflicting_flags]

        if used_conflicts:
            p.error(f"--preset cannot be combined with: {', '.join(used_conflicts)}")

    return args


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
    buffer = max(0, args.auto)
    # keep steady cadence using monotonic time
    next_tick = time.monotonic()
    while True:
        clear()
        s, n = choose_prompt(args)
        print(f"String: {s}, Note: {n}")
        print("\nCtrl + C to quit.")
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
        

def run_preset(args: argparse.Namespace) -> None:
    buffer = max(0, args.preset)
    next_tick = time.monotonic()
    index = 3
    n = NOTES_NATURAL[index]
    while True:
        for i in range(1, 7):
            clear()
            print(f"String: {i}, Note: {n}")
            print("\nCtrl + C to quit.")
            next_tick += buffer
            time.sleep(max(0.0, next_tick - time.monotonic()))
        index = (index + 4) % len(NOTES_NATURAL)
        n = NOTES_NATURAL[index]


def main() -> None:
    args = parse_args()

    try:
        if args.preset is not None:
            run_preset(args)
        elif args.auto is not None:
            run_auto(args)
        else:
            run_manual(args)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
