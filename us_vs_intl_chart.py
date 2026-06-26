"""
US vs. specific international markets — two views:
  Left:  ~10-year annualized USD total return (2015/16 -> end-2025)  [approximate]
  Right: 2025 calendar-year return (local headline index)
Illustrative/approximate figures for education; not investment advice.
"""
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    "figure.facecolor": "#0e1117",
    "axes.facecolor": "#0e1117",
    "axes.edgecolor": "#3a3f4b",
    "axes.labelcolor": "#d0d3da",
    "text.color": "#e6e6e6",
    "xtick.color": "#c2c6cf",
    "ytick.color": "#c2c6cf",
    "font.size": 11,
})

US_BLUE = "#42a5f5"
GREEN = "#26a69a"
RED = "#ef5350"
GREY = "#7c828d"

# ---- 10-year annualized USD total return (approximate) ----
ten_yr = [
    ("United States", 12.6),
    ("India",          8.0),
    ("Japan",          6.5),
    ("Canada",         6.5),
    ("Australia",      5.5),
    ("Germany",        5.5),
    ("UK",             4.5),
    ("China",          3.0),
]
ten_yr.sort(key=lambda t: t[1])  # ascending for horizontal bars

# ---- 2025 calendar-year return (headline index) ----
y2025 = [
    ("South Korea", 76.0),
    ("Japan",       26.0),
    ("Germany",     23.0),
    ("United States",17.0),
    ("India",       -1.6),
]
y2025.sort(key=lambda t: t[1])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6.6))

# ---------------- LEFT: 10-year ----------------
names1 = [t[0] for t in ten_yr]
vals1 = [t[1] for t in ten_yr]
colors1 = [US_BLUE if n == "United States" else GREY for n in names1]
bars1 = ax1.barh(names1, vals1, color=colors1, height=0.62)
ax1.axvline(12.6, color=US_BLUE, ls="--", lw=1, alpha=0.5)
for b, v in zip(bars1, vals1):
    ax1.text(v + 0.2, b.get_y() + b.get_height()/2, f"{v:.1f}%",
             va="center", ha="left", fontsize=10, color="#e6e6e6")
ax1.set_title("~10-Year Annualized Return (USD)\n2015/16 → end-2025  ·  approximate",
              fontsize=12.5, weight="bold", pad=10)
ax1.set_xlabel("Annualized total return, % per year")
ax1.set_xlim(0, 15)
ax1.grid(True, axis="x", color="#1c2230", lw=0.6)
for s in ["top", "right"]:
    ax1.spines[s].set_visible(False)
ax1.text(12.6, -0.9, "US benchmark", color=US_BLUE, fontsize=8.5, ha="center")

# ---------------- RIGHT: 2025 ----------------
names2 = [t[0] for t in y2025]
vals2 = [t[1] for t in y2025]
colors2 = []
for n, v in y2025:
    if n == "United States":
        colors2.append(US_BLUE)
    elif v < 0:
        colors2.append(RED)
    else:
        colors2.append(GREEN)
bars2 = ax2.barh(names2, vals2, color=colors2, height=0.6)
ax2.axvline(0, color="#3a3f4b", lw=1)
ax2.axvline(17.0, color=US_BLUE, ls="--", lw=1, alpha=0.5)
for b, v in zip(bars2, vals2):
    off = 1.2 if v >= 0 else -1.2
    ha = "left" if v >= 0 else "right"
    ax2.text(v + off, b.get_y() + b.get_height()/2, f"{v:+.1f}%",
             va="center", ha=ha, fontsize=10, color="#e6e6e6")
ax2.set_title("2025 Calendar-Year Return\nthe reversal · headline index",
              fontsize=12.5, weight="bold", pad=10)
ax2.set_xlabel("Total return, %")
ax2.set_xlim(-12, 88)
ax2.grid(True, axis="x", color="#1c2230", lw=0.6)
for s in ["top", "right"]:
    ax2.spines[s].set_visible(False)

fig.suptitle("US vs. International Markets — the Decade vs. the 2025 Flip",
             fontsize=15, weight="bold", y=0.99)
fig.text(0.5, 0.005,
         "Approximate USD figures for education only — not investment advice. "
         "Country single-year returns are local headline indices.",
         ha="center", fontsize=8.5, color="#8b909a")
fig.tight_layout(rect=[0, 0.02, 1, 0.96])
fig.savefig("/home/user/great_files/diagram_4_us_vs_intl.png", dpi=140)
print("Saved diagram_4_us_vs_intl.png")
