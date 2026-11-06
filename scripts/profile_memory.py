"""In a fresh process: python profile_memory.py OUT.json {cpu,cuda} GENERATOR.py [args...].
Use a scratch working directory: the original generator also writes audio there.
"""
import json
import resource
import runpy
import sys
from pathlib import Path

out, device, script, *args = sys.argv[1:]
sys.argv = [script, *args]
runpy.run_path(script, run_name="__main__")
metrics = {}
if device == "cuda":
    import torch
    torch.cuda.synchronize()
    metrics["cuda_allocated_bytes"] = torch.cuda.max_memory_allocated()
    metrics["cuda_reserved_bytes"] = torch.cuda.max_memory_reserved()
elif device != "cpu":
    raise ValueError(device)
rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
metrics["process_peak_rss_bytes"] = rss if sys.platform == "darwin" else rss * 1024
Path(out).write_text(json.dumps(metrics, indent=2) + "\n")
