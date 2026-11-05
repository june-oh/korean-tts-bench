"""Plot one observation per published clip. Run at the repository root."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

dest = Path("figures")
dest.mkdir(exist_ok=True)
models = json.loads(Path("models.json").read_text())
samples = []
for model in models:
    folder = Path("audio")/model["id"]
    first_file = folder/"first_audio.json"
    first = json.loads(first_file.read_text()) if first_file.exists() else {}
    for row in json.loads((folder/"measurements.json").read_text())["rows"]:
        total = row["seconds"][0] if row["seconds"] else None
        samples.append(dict(model=model["name"], prompt=row["id"], duration_s=row["duration"],
                            completion_s=total, rtf=total/row["duration"] if total else None,
                            first_audio_ms=1000*first[row["id"]] if row["id"] in first else None))
with (dest/"timings.csv").open("w",newline="") as f:
    writer = csv.DictWriter(f, fieldnames=samples[0]); writer.writeheader(); writer.writerows(samples)

color="#28688a"
for key, xlabel in [("completion_s","Full generation time (s)"),("rtf","Real-time factor"),
                    ("first_audio_ms","Time to first audio chunk (ms)")]:
    series = []
    for model in models:
        vals = [r[key] for r in samples if r["model"]==model["name"] and r[key] is not None]
        if vals:
            series.append((model["name"],np.array(vals)))
    if not series:
        continue
    fig,ax = plt.subplots(figsize=(8.7,1.2+0.62*len(series)))
    fig.subplots_adjust(left=.30,right=.97,top=.9,bottom=.64/fig.get_figheight())
    xmax=max(values.max() for _,values in series)
    for i,(name,values) in enumerate(series):
        ax.hlines(i,values.min(),values.max(),color="#7291a1",lw=2,zorder=1)
        offsets=np.random.default_rng(101+i).permutation(np.linspace(-.15,.15,len(values)))
        ax.scatter(values,i+offsets,s=21,color="#7caaba",alpha=.85,edgecolors="white",linewidths=.4)
        avg=values.mean()
        ax.scatter(avg,i,s=55,marker="D",color="#112d48",edgecolors="white",linewidths=.6,zorder=4)
        ax.annotate(f"{avg:.2f}",(avg,i),xytext=(0,9),textcoords="offset points",
                    ha="center",fontsize=9,color="#112d48")
    ax.set_yticks(range(len(series)),[f"{name}  (n={len(x)})" for name,x in series],fontsize=10)
    ax.set_ylim(len(series)-.58,-.55)
    ax.set_xlim(0,xmax*1.07)
    if key=="rtf":
        ax.axvline(1,ls="--",color="#ae723b",lw=1)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=7))
    ax.set_xlabel(xlabel)
    ax.grid(axis="x",color="#e1e7ea")
    ax.set_axisbelow(True)
    for spine in ("top","right","left"): ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y",length=0,pad=8)
    fig.savefig(dest/(key+".svg"),bbox_inches="tight",metadata={"Date":None})
    plt.close(fig)
