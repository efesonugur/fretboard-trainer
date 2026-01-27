import math
import os
import subprocess

# Folder containing the 12 source WAVs from the repo (C, C#, D, ..., B)
IN_DIR = "input_wav"
OUT_DIR = "out_E2_to_E5"
os.makedirs(OUT_DIR, exist_ok=True)

# Assumption: the repo provides ONE octave worth of pitch classes as files:
# C.wav, C#.wav, D.wav, ..., B.wav
# If your filenames differ (e.g., "Cs.wav" instead of "C#.wav"), adjust this map.
PITCH_CLASS_FILES = {
    "C":  "c1.wav",
    "C#": "c1s.wav",
    "D":  "d1.wav",
    "D#": "d1s.wav",
    "E":  "e1.wav",
    "F":  "f1.wav",
    "F#": "f1s.wav",
    "G":  "g1.wav",
    "G#": "g1s.wav",
    "A":  "a1.wav",
    "A#": "a1s.wav",
    "B":  "b1.wav",
}

PITCH_CLASS_TO_SEMITONE = {"C":0,"C#":1,"D":2,"D#":3,"E":4,"F":5,"F#":6,"G":7,"G#":8,"A":9,"A#":10,"B":11}
SEMITONE_TO_NAME_SHARP = {v:k for k,v in PITCH_CLASS_TO_SEMITONE.items()}

# We need E2..E5 inclusive => MIDI 40..76
# (E2=40, ..., E5=76)
MIDI_START = 40
MIDI_END   = 76

# We treat the repo's source octave as pitch classes only.
# We'll "anchor" them at octave 4 for calculating shifts (common convention: C4 is middle C).
# That means: source pitch class X is considered X4 (MIDI = 12*(4+1)+pc = 60+pc).
SRC_OCTAVE = 4
SRC_BASE_MIDI_C4 = 12 * (SRC_OCTAVE + 1)  # 60

def midi_to_name(midi: int) -> str:
    pc = midi % 12
    octave = midi // 12 - 1
    return f"{SEMITONE_TO_NAME_SHARP[pc]}{octave}"

for midi in range(MIDI_START, MIDI_END + 1):
    pc = midi % 12
    pc_name = SEMITONE_TO_NAME_SHARP[pc]

    src_file = os.path.join(IN_DIR, PITCH_CLASS_FILES[pc_name])
    if not os.path.exists(src_file):
        raise FileNotFoundError(f"Missing source file for {pc_name}: {src_file}")

    # semitone shift relative to the assumed source note in octave 4
    src_midi = SRC_BASE_MIDI_C4 + pc
    shift_semitones = midi - src_midi

    # pitch ratio for Rubber Band
    pitch_ratio = 2 ** (shift_semitones / 12)

    out_name = midi_to_name(midi).replace("#", "s") + ".wav"  # e.g. F#2 -> Fs2.wav
    out_path = os.path.join(OUT_DIR, out_name)

    # FFmpeg + rubberband filter (changes pitch while keeping duration roughly constant)
    cmd = [
        "ffmpeg", "-y",
        "-i", src_file,
        "-af", f"rubberband=pitch={pitch_ratio}",
        out_path
    ]
    subprocess.run(cmd, check=True)

print(f"Done. Wrote {MIDI_END - MIDI_START + 1} files to: {OUT_DIR}")
