"""Run at repository root after collecting figures/memory.json."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

data = json.loads(Path("figures/memory.json").read_text())["models"]
host = [(row["name"],row["process_peak_rss_bytes"]/2**30) for row in data if "process_peak_rss_bytes" in row]
gpu = [row for row in data if "cuda_reserved_bytes" in row]
fig, axes = plt.subplots(1,2, figsize=(10.8,4.0), layout="constrained")
for ax, vals, title in zip(axes,[host,[(r["name"],r["cuda_reserved_bytes"]/2**30) for r in gpu]],["Host RAM · process peak RSS","GPU memory · PyTorch allocator"]):
    labels, values = zip(*vals)
    ax.set_axisbelow(True)
    ax.grid(axis="x",alpha=.16)
    ax.barh(labels,values,height=.46,color="#324383" if ax==axes[0] else "#c2d2df",label="Peak reserved")
    ax.invert_yaxis()
    ax.set_title(title,loc="left",fontsize=12,fontweight="bold")
    ax.set_xlabel("GiB")
    ax.set_xlim(0,max(values)*1.28)
    for idx,val in enumerate(values):
        ax.text(val+max(values)*.025,idx,f"{val:.2f}",va="center",fontsize=9)
    for key in ("right","top","left"): ax.spines[key].set_visible(False)
axes[1].barh([r["name"] for r in gpu],[r["cuda_allocated_bytes"]/2**30 for r in gpu],height=.20,color="#197467",label="Peak allocated")
axes[1].legend(loc="lower center",bbox_to_anchor=(.5,-.37),ncol=2,frameon=False,fontsize=8)
fig.savefig("figures/memory.svg")
