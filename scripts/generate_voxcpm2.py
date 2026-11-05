"""Run in a private directory with model/, prompts.json and a free CUDA GPU."""
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from voxcpm import VoxCPM

model = VoxCPM.from_pretrained(str(Path("model").resolve()), load_denoiser=False, optimize=False)
out = Path("result")
out.mkdir(exist_ok=True)
rate = model.tts_model.sample_rate

def synthesize(text, seed):
    torch.manual_seed(seed)
    chunks = []
    first = None
    torch.cuda.synchronize()
    start = time.perf_counter()
    for samples in model.generate_streaming(text=text, cfg_value=2.0, inference_timesteps=10,
                                           normalize=False, retry_badcase=False):
        if samples.size:
            if first is None:
                first = time.perf_counter() - start
            chunks.append(samples.reshape(-1))
    wave = np.concatenate(chunks)
    torch.cuda.synchronize()
    return wave, first, time.perf_counter() - start

synthesize("준비 운동을 시작합니다.", 0)
times, first_audio = {}, {}
for pid, _, text, _ in json.loads(Path("prompts.json").read_text()):
    wave, first, elapsed = synthesize(text, 100*int(pid[1:]))
    assert 0 < first <= elapsed and np.isfinite(wave).all() and np.abs(wave).max() > .001
    sf.write(out / (pid+".wav"), wave, rate, subtype="PCM_16")
    times[pid], first_audio[pid] = [elapsed], first
    print(pid, first, elapsed, len(wave)/rate, flush=True)
for name, data in [("times", times), ("first_audio", first_audio)]:
    (out/(name+".json")).write_text(json.dumps(data, indent=2))
