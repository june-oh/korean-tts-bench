"""Generate a private staging folder; never publishes. Standard library only."""
import argparse
import json
import os
import time
import urllib.request
from pathlib import Path
from urllib.parse import quote

parser = argparse.ArgumentParser()
parser.add_argument("voice_id")
parser.add_argument("folder", type=Path)
parser.add_argument("--model", default="eleven_multilingual_v2")
args = parser.parse_args()
secret = os.environ.get("ELEVENLABS_API_KEY")
if not secret:
    parser.error("set ELEVENLABS_API_KEY in the local environment")
prompts = json.loads(Path("prompts.json").read_text())
args.folder.mkdir(parents=True, exist_ok=True)
manifest = args.folder / "run.json"
config = dict(voice=args.voice_id, model=args.model, prompts=prompts, output_format="mp3_44100_128")
if manifest.exists() and json.loads(manifest.read_text()) != config:
    parser.error("use a new folder for changed inputs")
manifest.write_text(json.dumps(config,ensure_ascii=False))
url = "https://api.elevenlabs.io/v1/text-to-speech/"+quote(args.voice_id,safe="")+"?output_format=mp3_44100_128"
for pid, _, text, _ in prompts:
    clip = args.folder / (pid+".mp3")
    if clip.exists():
        continue
    body = json.dumps(dict(text=text,model_id=args.model)).encode()
    req = urllib.request.Request(url,body,{"xi-api-key":secret,"Content-Type":"application/json","Accept":"audio/mpeg"})
    start = time.perf_counter()
    with urllib.request.urlopen(req,timeout=120) as resp:
        audio = resp.read()
    elapsed = time.perf_counter()-start
    if not audio:
        raise RuntimeError("empty audio response")
    (args.folder / (pid+".seconds")).write_text(str(elapsed))
    tmp = clip.with_suffix(".tmp")
    tmp.write_bytes(audio)
    tmp.replace(clip)
times = {p[0]:[float((args.folder/(p[0]+".seconds")).read_text())] for p in prompts}
(args.folder/"times.json").write_text(json.dumps(times,indent=2))
