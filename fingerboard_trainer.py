import argparse
import random
import time
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import platform
import sys
from typing import List, Sequence
import warnings
warnings.filterwarnings("ignore", module="pygame.pkgdata")
import pygame

# audio stuff
# ------------------------------------------------------------------------------------------
def init_audio(wav_path: str):
    os.environ.setdefault("SDL_AUDIODRIVER", "pulseaudio")
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.init()
    pygame.mixer.init()
    return pygame.mixer.Sound(wav_path)

class Ding:
    def __init__(self, wav_path: str):
        self._sound = init_audio(wav_path)

    def play(self, block: bool = False):
        ch = self._sound.play()
        if block and ch is not None:
            while ch.get_busy():
                pygame.time.wait(10)

    def close(self):
        try:
            pygame.mixer.quit()
            pygame.quit()
        except Exception:
            pass

# ------------------------------------------------------------------------------------------

STRINGS: List[int] = [1, 2, 3, 4, 5, 6]
NOTES: List[str] = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NOTES_NATURAL: List[str] = ["C", "D", "E", "F", "G", "A", "B"]

DEFAULT_TIME = 1  # seconds

DOWNBEAT_PATH = "Synth_Weird_E_lo.wav"
if not os.path.exists(DOWNBEAT_PATH):
    print(f"File not found: {DOWNBEAT_PATH}")
    sys.exit(1)

#SECONDARY_BEAT = ""
#if not os.path.exists(SECONDARY_BEAT):
#    print(f"File not found: {SECONDARY_BEAT}")
#    sys.exit(1)


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


def run_auto(args: argparse.Namespace, downbeat: Ding) -> None:
    buffer = max(0, args.auto)
    # keep steady cadence using monotonic time
    next_tick = time.monotonic()
    while True:
        clear()
        s, n = choose_prompt(args)
        print(f"String: {s}, Note: {n}")
        print("\nCtrl + C to quit.")
        downbeat.play(block=False)
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
        

def run_preset(args: argparse.Namespace, downbeat: Ding) -> None:
    buffer = max(0, args.preset)
    next_tick = time.monotonic()
    index = 3
    n = NOTES_NATURAL[index]
    while True:
        for i in range(1, 7):
            clear()
            print(f"String: {i}, Note: {n}")
            print("\nCtrl + C to quit.")
            downbeat.play(block=False)
            next_tick += buffer
            time.sleep(max(0.0, next_tick - time.monotonic()))
        index = (index + 4) % len(NOTES_NATURAL)
        n = NOTES_NATURAL[index]

def main() -> None:
    args = parse_args()

    downbeat = Ding(DOWNBEAT_PATH)

    try:
        if args.preset is not None:
            run_preset(args, downbeat=downbeat)
        elif args.auto is not None:
            run_auto(args, downbeat=downbeat)
        else:
            run_manual(args)
    except KeyboardInterrupt:
        print("\nStopped.")

    finally:
        downbeat.close()

if __name__ == "__main__":
    main()
