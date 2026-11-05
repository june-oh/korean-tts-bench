"""Run with one free CUDA GPU exposed through CUDA_VISIBLE_DEVICES."""
import argparse
import json
import time
from importlib.metadata import version
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel

parser = argparse.ArgumentParser()
parser.add_argument("model_dir", type=Path)
parser.add_argument("prompts", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
model = Qwen3TTSModel.from_pretrained(str(args.model_dir.resolve()), device_map="cuda:0",
                                      dtype=torch.bfloat16, attn_implementation="sdpa")
def synth(text, seed):
    torch.manual_seed(seed)
    torch.cuda.synchronize()
    start = time.perf_counter()
    with torch.inference_mode():
        waves, rate = model.generate_custom_voice(text=text, language="Korean", speaker="Sohee",
                                                  max_new_tokens=600)
    torch.cuda.synchronize()
    return waves[0], rate, time.perf_counter() - start

synth("준비 운동을 시작합니다.", 0)
times = {}
for pid, _, text, _ in json.loads(args.prompts.read_text()):
    audio, rate, seconds = synth(text, 100 * int(pid[1:]))
    assert np.isfinite(audio).all() and np.abs(audio).max() > 0.001
    sf.write(args.output / (pid + ".wav"), audio, rate, subtype="PCM_16")
    times[pid] = [seconds]
    print(pid, round(seconds, 3), len(audio)/rate, flush=True)
(args.output / "times.json").write_text(json.dumps(times, indent=2))
print(torch.cuda.get_device_name(), torch.__version__, version("qwen-tts"), torch.cuda.max_memory_allocated(), flush=True)
