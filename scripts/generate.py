"""Run from the repository root, with a prepared asset directory."""
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

assets = Path(sys.argv[1]).resolve()
engine = sys.argv[2]
sys.path.insert(0, str(assets))
if engine == "supertonic3":
    from helper import load_text_to_speech, load_voice_style
    root = assets / "s3"
    model = load_text_to_speech(str(root / "onnx"))
    style = load_voice_style([str(root / "voice_styles/F1.json")])
    rate = model.sample_rate

    def synth(text):
        samples, duration = model(text, "ko", style, 8, 1.0)
        return samples[0, :int(rate * duration[0].item())]
elif engine == "mms":
    import torch
    from transformers import AutoTokenizer, VitsModel
    root = assets / "mms"
    torch.set_num_threads(4)
    model = VitsModel.from_pretrained(root).eval()
    tokenizer = AutoTokenizer.from_pretrained(root)
    rate = model.config.sampling_rate

    @torch.inference_mode()
    def synth(text):
        return model(**tokenizer(text, return_tensors="pt")).waveform[0].numpy()
else:
    raise ValueError(engine)
out = Path("audio") / engine
out.mkdir(exist_ok=True, parents=True)
synth("준비 운동을 시작합니다.")
rows = []
for pid, _, text, _ in json.loads(Path("prompts.json").read_text()):
    times = []
    for trial in range(3):
        seed = 100 * int(pid[1:]) + trial
        np.random.seed(seed)
        if engine == "mms":
            torch.manual_seed(seed)
        start = time.perf_counter()
        wave = synth(text)
        times.append(round(time.perf_counter() - start, 5))
        if trial == 0:
            assert np.isfinite(wave).all() and np.max(np.abs(wave)) > 0.001
            sf.write(out / (pid + ".wav"), wave, rate, subtype="PCM_16")
            duration = len(wave) / rate
    rows.append(dict(id=pid, seconds=times, duration=duration, rate=rate))
    print(engine, pid, times, flush=True)
(out / "measurements.json").write_text(json.dumps(dict(revision=(root / "revision").read_text().strip(), rows=rows),indent=2))
