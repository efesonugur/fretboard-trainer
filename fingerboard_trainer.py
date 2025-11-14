import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
os.environ.setdefault("SDL_AUDIODRIVER", "pulseaudio")

import warnings
warnings.filterwarnings("ignore", module="pygame.pkgdata")

import argparse
import random
import time
import platform
import sys
from typing import List, Sequence

import pygame

# audio stuff
# ------------------------------------------------------------------------------------------
def init_audio(wav_path: str):
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

DEFAULT_BPM = 180  # BPM

DOWNBEAT_PATH = "Perc_MetronomeQuartz_hi.wav"
if not os.path.exists(DOWNBEAT_PATH):
    print(f"File not found: {DOWNBEAT_PATH}")
    sys.exit(1)

SECONDARY_BEAT_PATH = "Perc_MetronomeQuartz_lo.wav"
if not os.path.exists(SECONDARY_BEAT_PATH):
    print(f"File not found: {SECONDARY_BEAT_PATH}")
    sys.exit(1)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Guitar fretboard trainer")
    p.add_argument(
        "--auto",
        nargs="?",
        type=int,
        metavar="BPM",
        const=DEFAULT_BPM,
        help="run automatically N beats-per-minute",
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
        metavar="BPM",
        const=DEFAULT_BPM,
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


def visual(beat: int, string: int, note: str) -> None:
    BOLD = "\033[1m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"
    #SPHERE = "\u2B24"
    BLOCK = "\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588"
    
    clear()
    print(f"String: {string}, Note: {note}\n")
    
    match beat:
        case (0):
            print(f"{BOLD}{RED}{BLOCK}{RESET}")
        case (1):
            print(f"{BOLD}{RED}{BLOCK}{RESET} {BOLD}{MAGENTA}{BLOCK}{RESET}")
        case (2):
            print(f"{BOLD}{RED}{BLOCK}{RESET} {BOLD}{MAGENTA}{BLOCK} {BLOCK}{RESET}")
        case (3):
            print(f"{BOLD}{RED}{BLOCK}{RESET} {BOLD}{MAGENTA}{BLOCK} {BLOCK} {BLOCK}{RESET}")

    print("\nCtrl + C to quit.")
    return


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


def run_auto(args: argparse.Namespace, downbeat: Ding, secondary_beat: Ding) -> None:
    period = 60.0 / args.auto
    period = max(0.001, period)

    start = time.monotonic()
    beat_idx = 0

    while True:
        for j in range(4):
            target = start + beat_idx * period
            now = time.monotonic()
            remaining = target - now

            if remaining > 0:
                if remaining > 0.003:
                    time.sleep(remaining - 0.002)
                
                # Fine wait loop without burning 100% CPU
                while True:
                    now = time.perf_counter()
                    if now >= target:
                        break
                    if target - now > 0.0005:
                        time.sleep(0.0005)

            if j == 0:
                s, n = choose_prompt(args)
                downbeat.play(block=False)
            else:
                secondary_beat.play(block=False)
            
            visual(beat=j, string=s, note=n)

            beat_idx += 1

        
def run_preset(args: argparse.Namespace, downbeat: Ding, secondary_beat: Ding) -> None:
    period = 60.0 / args.preset
    period = max(0.001, period)

    start = time.monotonic()
    beat_idx = 0 

    index = 3
    n = NOTES_NATURAL[index]

    while True:
        for i in range(1, 7):
            for j in range(4):
                # 1. compute ideal time for this beat
                target = start + beat_idx * period
                
                # 2. sleep until that time (with small coarse sleep)
                now = time.monotonic()
                remaining = target - now

                if remaining > 0:
                    if remaining > 0.003:
                        time.sleep(remaining - 0.002)

                    # Fine wait loop without burning 100% CPU
                    while True:
                        now = time.perf_counter()
                        if now >= target:
                            break
                        if target - now > 0.0005:
                            time.sleep(0.0005)
                
                # 3. fire the beat at the scheduled time
                if j == 0:
                    downbeat.play(block=False)
                else:
                    secondary_beat.play(block=False)

                visual(beat=j, string=i, note=n)

                beat_idx += 1

        index = (index + 4) % len(NOTES_NATURAL)
        n = NOTES_NATURAL[index]


# def run_preset_old(args: argparse.Namespace, downbeat: Ding, secondary_beat: Ding) -> None:
#     period = 60.0 / args.preset
#     period = max(0.001, period)

#     next_tick = time.monotonic()
#     index = 3
#     n = NOTES_NATURAL[index]
#     while True:
#         for i in range(1, 7):
#             for j in range(4):
#                 if j == 0:
#                     downbeat.play(block=False)
#                 else:
#                     secondary_beat.play(block=True)
#                 visual(beat=j, string=i, note=n)
#                 next_tick += period
#                 now = time.monotonic()
#                 if next_tick <= now:
#                     missed = int((now - next_tick) // period) + 1
#                     next_tick += missed * period
#                 time.sleep(max(0.0, next_tick - time.monotonic()))

#         index = (index + 4) % len(NOTES_NATURAL)
#         n = NOTES_NATURAL[index]


def main() -> None:
    args = parse_args()

    downbeat = Ding(DOWNBEAT_PATH)
    secondary_beat = Ding(SECONDARY_BEAT_PATH)

    try:
        if args.preset is not None:
            run_preset(args, downbeat, secondary_beat)
        elif args.auto is not None:
            run_auto(args, downbeat, secondary_beat)
        else:
            run_manual(args)
    except KeyboardInterrupt:
        print("\nStopped.")

    finally:
        downbeat.close()

if __name__ == "__main__":
    main()
