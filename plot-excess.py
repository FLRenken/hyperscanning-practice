## AI GENERATED
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

df = pd.read_csv('plv_condition_results.csv')
out = 'excess-plv.png'
w = df.pivot(index="subject", columns="condition", values="excess_PLV")[["duet", "constant_pitch"]]
labels = ["Duet", "Constant pitch"]
colors = ["#2a6fdb", "#e07b39"]

fig, ax = plt.subplots(figsize=(5.2, 5.2), dpi=200)
ax.axhline(0, color="#888", lw=1, ls="--", zorder=0)
rng = np.random.default_rng(0)
jit = rng.uniform(-0.06, 0.06, len(w))
x0, x1 = 0 + jit, 1 + jit
for a, b, ya, yb in zip(x0, x1, w["duet"], w["constant_pitch"]):
    ax.plot([a, b], [ya, yb], color="#bbb", lw=0.7, zorder=1)
for i, (col, c) in enumerate(zip(w.columns, colors)):
    y = w[col].values
    ax.scatter(i + jit, y, s=22, color=c, alpha=0.75, edgecolor="white", lw=0.5, zorder=2)
    m, se = y.mean(), stats.sem(y)
    h = se * stats.t.ppf(0.975, len(y) - 1)
    ax.errorbar(i + 0.28, m, yerr=h, fmt="o", color="black", ms=6, capsize=4, lw=1.5, zorder=3)
    ax.text(i + 0.28, m + h + 0.0005, f"{m:+.4f}\n[{m-h:+.4f}, {m+h:+.4f}]", ha="center", va="bottom", fontsize=7)
ax.set_xticks([0, 1], labels)
ax.set_xlim(-0.4, 1.6)
ax.set_ylabel("Excess PLV (real − shuffled)")
ax.set_title(f"Theta-band excess PLV per dyad (N = {len(w)})\nmean ± 95% CI; lines connect the same dyad", fontsize=9)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(out)
print(w.describe())