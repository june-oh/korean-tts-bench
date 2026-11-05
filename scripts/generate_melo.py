"""Run with the official MeloTTS source on PYTHONPATH and its KR import patch."""
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from melo.api import TTS

model = TTS(language="KR",device="cuda",config_path="model/config.json",ckpt_path="model/checkpoint.pth")
out = Path("result")
out.mkdir(exist_ok=True)
def generate(text, seed):
    torch.manual_seed(seed)
    torch.cuda.synchronize()
    start=time.perf_counter()
    wave=model.tts_to_file(text, model.hps.data.spk2id.KR, quiet=True)
    torch.cuda.synchronize()
    return wave, time.perf_counter()-start
generate("준비 운동을 시작합니다.",0)
times,failed={},{}
for pid, _, text, _ in json.loads(Path("prompts.json").read_text()):
    try:
        wave,sec=generate(text,int(pid[1:])*100)
    except (KeyError,AssertionError,IndexError) as error:
        failed[pid]=repr(error)
        print(pid,repr(error),flush=True)
        continue
    assert np.max(np.abs(wave))>.001 and np.isfinite(wave).all()
    sf.write(out/(pid+".wav"),wave,model.hps.data.sampling_rate,subtype="PCM_16")
    times[pid]=[sec]
    print(pid,sec,flush=True)
(out/"times.json").write_text(json.dumps(times,indent=2))
(out/"failures.json").write_text(json.dumps(failed,ensure_ascii=False,indent=2))
