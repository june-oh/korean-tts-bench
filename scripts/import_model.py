"""Add one model from a private staging directory, after author review."""
import argparse
import json
import math
import re
import shutil
import wave
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("folder", type=Path, help="model.json, optional times.json, P01.wav ...")
args = p.parse_args()
folder = args.folder
meta = json.loads((folder / "model.json").read_text())
fields = ["id", "name", "voice", "device", "url", "license", "revision", "publication_basis"]
if not all(isinstance(meta.get(k), str) and meta[k].strip() for k in fields):
    p.error("model.json is missing provenance or publication terms")
key = meta["id"]
if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", key):
    p.error("invalid model id")
models = json.loads(Path("models.json").read_text())
out = Path("audio") / key
if out.exists() or any(m["id"] == key for m in models):
    p.error("choose a new model/voice run id")
prompts = json.loads(Path("prompts.json").read_text())
times = json.loads((folder / "times.json").read_text()) if (folder / "times.json").exists() else {}
rows = []
for pid, *_ in prompts:
    file = folder / (pid + ".wav")
    if not file.exists():
        continue
    with wave.open(str(file)) as w:
        if w.getcomptype() != "NONE" or not w.getnframes():
            p.error("expected nonempty PCM WAV")
        row = dict(id=pid, rate=w.getframerate(), duration=w.getnframes()/w.getframerate(), seconds=times.get(pid, []))
    if not isinstance(row["seconds"], list) or not all(isinstance(t,(int,float)) and math.isfinite(t) and t>0 for t in row["seconds"]):
        p.error("invalid timing samples")
    rows.append(row)
if not rows:
    p.error("no matching prompt WAVs")
out.mkdir()
try:
    for r in rows:
        shutil.copyfile(folder / (r["id"]+".wav"),out / (r["id"]+".wav"))
    (out/"measurements.json").write_text(json.dumps(dict(revision=meta["revision"],rows=rows),indent=2))
    temp = Path("models.json.tmp")
    temp.write_text(json.dumps(models+[meta], ensure_ascii=False, indent=2)+"\n")
    temp.replace("models.json")
except Exception:
    shutil.rmtree(out)
    raise
