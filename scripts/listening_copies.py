"""Encode listening copies, preserving the synthesis WAVs and timing data.

Pass an FFmpeg binary built with libmp3lame as the first argument.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ffmpeg = sys.argv[1]
target = -18.0
for model in json.loads(Path("models.json").read_text()):
    source = Path("audio") / model["id"]
    dest = Path("listen") / model["id"]
    dest.mkdir(parents=True, exist_ok=True)
    report = {}
    for wav in sorted(source.glob("*.wav")):
        measurement = subprocess.run(
            [ffmpeg, "-nostdin", "-i", str(wav), "-af", "loudnorm=print_format=json",
             "-f", "null", "-"], capture_output=True, text=True, check=True)
        stats = json.loads(re.search(r'\{\s*"input_i".*?\}', measurement.stderr, re.S)[0])
        integrated, peak = float(stats["input_i"]), float(stats["input_tp"])
        gain = min(target-integrated, -2.0-peak)
        subprocess.run([ffmpeg, "-nostdin", "-y", "-loglevel", "error", "-i", str(wav),
                        "-af", f"volume={gain:.3f}dB", "-codec:a", "libmp3lame",
                        "-ar", "44100", "-b:a", "128k", str(dest / (wav.stem+".mp3"))], check=True)
        report[wav.stem] = dict(input_lufs=integrated, input_true_peak_db=peak, gain_db=round(gain,3))
    (dest/"levels.json").write_text(json.dumps(report, indent=2))
