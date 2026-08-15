"""
Stress-test of the AI + robotics + crypto thesis as ONE portfolio.
Two panels:
  A) Illustrative correlation matrix -> the holdings are largely one bet
  B) Estimated drawdown in a ~-20% S&P correction (beta-scaled, illustrative)

ALL NUMBERS ARE ILLUSTRATIVE EDUCATIONAL ESTIMATES, not backtested data.
Colors use the dataviz reference palette (dark mode), validated set.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# ---- palette (dataviz reference, dark mode) ----
SURFACE = "#1a1a19"
INK = "#ffffff"
INK2 = "#c3c2b7"
MUTED = "#898781"
GRID = "#2c2c2a"
BLUE = "#3987e5"
RED = "#e66767"
CRIT = "#d03b3b"
ORANGE = "#d95926"

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": GRID,
    "text.color": INK,
    "axes.labelcolor": INK2,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "font.size": 11,
    "font.family": "sans-serif",
})

assets = ["NVDA", "AMD", "AMZN", "MU", "Robotics", "TAO", "BTC"]
n = len(assets)

# ---- illustrative correlation matrix ----
C = np.array([
    [1.00, 0.82, 0.68, 0.78, 0.70, 0.55, 0.58],
    [0.82, 1.00, 0.62, 0.80, 0.68, 0.52, 0.55],
    [0.68, 0.62, 1.00, 0.60, 0.60, 0.48, 0.52],
    [0.78, 0.80, 0.60, 1.00, 0.64, 0.50, 0.53],
    [0.70, 0.68, 0.60, 0.64, 1.00, 0.55, 0.57],
    [0.55, 0.52, 0.48, 0.50, 0.55, 1.00, 0.78],
    [0.58, 0.55, 0.52, 0.53, 0.57, 0.78, 1.00],
])

# sequential blue ramp (dark: high corr -> brighter blue = more present)
blue_ramp = LinearSegmentedColormap.from_list(
    "blues_dark", ["#12365f", "#184f95", "#256abf", "#3987e5", "#6da7ec", "#9ec5f4"])

# ---- illustrative drawdown in a ~-20% correction ----
dd = [
    ("S&P 500 (ref)", -20, MUTED),
    ("AMZN",          -26, BLUE),
    ("NVDA",          -35, RED),
    ("Robotics",      -40, RED),
    ("MU",            -42, RED),
    ("AMD",           -48, ORANGE),
    ("BTC",           -50, ORANGE),
    ("TAO",           -72, CRIT),
]
dd.sort(key=lambda t: t[1])  # most negative first -> bottom

fig, (axA, axB) = plt.subplots(1, 2, figsize=(13.5, 6.4),
                               gridspec_kw={"width_ratios": [1.05, 1.0], "wspace": 0.32})

# ================= PANEL A: correlation heatmap =================
im = axA.imshow(C, cmap=blue_ramp, vmin=0.4, vmax=1.0, aspect="equal")
axA.set_xticks(range(n)); axA.set_yticks(range(n))
axA.set_xticklabels(assets, rotation=45, ha="right", fontsize=10)
axA.set_yticklabels(assets, fontsize=10)
for i in range(n):
    for j in range(n):
        v = C[i, j]
        txt = "1.0" if v == 1.0 else f"{v:.2f}"
        color = "#0b0b0b" if v >= 0.72 else "#ffffff"
        axA.text(j, i, txt, ha="center", va="center", fontsize=8.6, color=color)
axA.set_title("A.  Correlation of the holdings\n(illustrative) — everything moves together",
              fontsize=12, weight="bold", color=INK, pad=12)
# thin surface gridlines between cells
axA.set_xticks(np.arange(-.5, n, 1), minor=True)
axA.set_yticks(np.arange(-.5, n, 1), minor=True)
axA.grid(which="minor", color=SURFACE, lw=2)
axA.tick_params(which="minor", length=0)
for s in axA.spines.values():
    s.set_visible(False)
cbar = fig.colorbar(im, ax=axA, fraction=0.046, pad=0.04)
cbar.set_label("correlation", color=INK2, fontsize=9)
cbar.ax.tick_params(colors=INK2, labelsize=8)
cbar.outline.set_edgecolor(GRID)

# ================= PANEL B: drawdown bars =================
names = [t[0] for t in dd]
vals = [t[1] for t in dd]
colors = [t[2] for t in dd]
ypos = np.arange(len(dd))
bars = axB.barh(ypos, vals, color=colors, height=0.66)
axB.set_yticks(ypos); axB.set_yticklabels(names, fontsize=10)
axB.axvline(0, color="#383835", lw=1)
axB.axvline(-20, color=MUTED, ls="--", lw=1, alpha=0.7)
for b, v in zip(bars, vals):
    axB.text(v - 1.5, b.get_y() + b.get_height()/2, f"{v}%",
             va="center", ha="right", fontsize=9.5, color=INK)
axB.set_title("B.  Est. drawdown in a ~-20% market correction\n(beta-scaled, illustrative)",
              fontsize=12, weight="bold", color=INK, pad=12)
axB.set_xlabel("Peak-to-trough %")
axB.set_xlim(-82, 4)
axB.grid(True, axis="x", color=GRID, lw=0.6)
axB.text(-20, -0.75, "market −20%", color=MUTED, fontsize=8, ha="center", va="center")
for s in ["top", "right", "left"]:
    axB.spines[s].set_visible(False)

fig.suptitle("Stress test — is AI + Robotics + Crypto three bets, or one?",
             fontsize=15, weight="bold", color=INK, y=1.02)
fig.text(0.5, 0.005,
         "Illustrative educational estimates — NOT backtested data or a forecast. "
         "Correlations & betas are assumptions to show structure, not measured values.",
         ha="center", fontsize=8.3, color=MUTED)
fig.tight_layout(rect=[0, 0.025, 1, 0.95])
fig.savefig("/home/user/great_files/diagram_5_stress_test.png", dpi=140)
print("Saved diagram_5_stress_test.png")
