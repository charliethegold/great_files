"""
Educational trading diagrams:
  1) Anatomy of a bull trap (false breakout) with stop-loss placement
  2) Real breakout vs. bull trap (volume confirmation)
  3) Bearish RSI divergence as an early warning
These are illustrative concept charts, not real market data.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

plt.rcParams.update({
    "figure.facecolor": "#0e1117",
    "axes.facecolor": "#0e1117",
    "axes.edgecolor": "#3a3f4b",
    "axes.labelcolor": "#d0d3da",
    "text.color": "#e6e6e6",
    "xtick.color": "#8b909a",
    "ytick.color": "#8b909a",
    "font.size": 11,
})

GREEN = "#26a69a"
RED = "#ef5350"
BLUE = "#42a5f5"
AMBER = "#ffb300"
GREY = "#6b7280"


# ---------------------------------------------------------------------------
# 1) ANATOMY OF A BULL TRAP
# ---------------------------------------------------------------------------
def bull_trap_anatomy():
    fig, ax = plt.subplots(figsize=(11, 6.2))
    x = np.arange(0, 100)
    resistance = 100.0

    price = np.full(100, 90.0)
    # approach resistance, consolidate
    price[0:25] = 84 + np.linspace(0, 6, 25) + np.random.RandomState(1).normal(0, 0.4, 25)
    price[25:45] = 96 + np.random.RandomState(2).normal(0, 0.8, 20)        # bumping the level
    # false breakout spike above resistance
    price[45:52] = np.linspace(99, 106, 7)
    # sharp reversal back down through resistance -> the trap
    price[52:70] = np.linspace(106, 88, 18)
    price[70:100] = np.linspace(88, 74, 30) + np.random.RandomState(3).normal(0, 0.5, 30)

    ax.plot(x, price, color="#e6e6e6", lw=1.8)

    # resistance line
    ax.axhline(resistance, color=AMBER, ls="--", lw=1.5, alpha=0.9)
    ax.text(1, resistance + 0.6, "RESISTANCE", color=AMBER, fontsize=10, weight="bold")

    # breakout zone
    ax.scatter([48], [105.6], color=GREEN, s=70, zorder=5)
    ax.annotate("False breakout\n(buyers pile in)", xy=(48, 105.6), xytext=(20, 110),
                color=GREEN, fontsize=10, ha="center",
                arrowprops=dict(arrowstyle="->", color=GREEN))

    # the trap reversal
    ax.scatter([60], [96], color=RED, s=70, zorder=5)
    ax.annotate("Reversal back below\nresistance = THE TRAP",
                xy=(60, 96), xytext=(78, 104),
                color=RED, fontsize=10, ha="center",
                arrowprops=dict(arrowstyle="->", color=RED))

    # trapped buyers region
    ax.axvspan(45, 52, color=GREEN, alpha=0.08)
    ax.text(85, 78, "Trapped longs\nsell in loss →\nfuels the drop",
            color=RED, fontsize=9, ha="center")

    # safe stop-loss placement
    ax.axhline(94.5, color=BLUE, ls=":", lw=1.4, alpha=0.9)
    ax.text(1, 94.5 + 0.5, "STOP-LOSS (just below the level)", color=BLUE, fontsize=9, weight="bold")

    ax.set_title("Anatomy of a Bull Trap (False Breakout)", fontsize=14, weight="bold", pad=12)
    ax.set_xlabel("Time")
    ax.set_ylabel("Price")
    ax.set_ylim(70, 114)
    ax.grid(True, color="#1c2230", lw=0.6)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig("/home/user/great_files/diagram_1_bull_trap.png", dpi=140)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2) REAL BREAKOUT vs BULL TRAP  (volume confirmation)
# ---------------------------------------------------------------------------
def breakout_vs_trap():
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 7),
                             gridspec_kw={"height_ratios": [3, 1], "hspace": 0.08, "wspace": 0.18})
    rs = np.random.RandomState(7)
    res = 100.0

    for col, (title, real) in enumerate([("REAL BREAKOUT", True), ("BULL TRAP", False)]):
        ax = axes[0, col]
        axv = axes[1, col]
        x = np.arange(60)

        p = np.full(60, 95.0)
        p[0:30] = 92 + rs.normal(0, 0.8, 30)
        if real:
            p[30:60] = np.linspace(100, 116, 30) + rs.normal(0, 0.6, 30)
            vol = np.concatenate([rs.uniform(3, 6, 30), rs.uniform(8, 13, 30)])  # volume EXPANDS
            line_c = GREEN
            note = "Closes hold above\n+ volume expands\n= trust it"
        else:
            p[30:38] = np.linspace(100, 104, 8)
            p[38:60] = np.linspace(104, 88, 22) + rs.normal(0, 0.5, 22)
            vol = np.concatenate([rs.uniform(3, 6, 30), rs.uniform(2.5, 4.5, 30)])  # volume WEAK
            line_c = RED
            note = "Weak volume on break\n+ fails to hold\n= the trap"

        ax.plot(x, p, color="#e6e6e6", lw=1.7)
        ax.axhline(res, color=AMBER, ls="--", lw=1.3)
        ax.text(1, res + 0.6, "resistance", color=AMBER, fontsize=8.5)
        ax.set_title(title, color=line_c, fontsize=12.5, weight="bold")
        ax.set_ylim(84, 120)
        ax.set_xticks([])
        ax.text(30, 117 if real else 117, note, color=line_c, fontsize=9, ha="center")
        ax.grid(True, color="#1c2230", lw=0.5)
        for s in ["top", "right"]:
            ax.spines[s].set_visible(False)

        vcolors = [GREEN if real else GREY] * 30
        vcolors = [GREY] * 30 + ([GREEN] * 30 if real else [RED] * 30)
        axv.bar(x, vol, color=vcolors, width=0.9)
        axv.axvline(29.5, color="#555", ls=":", lw=1)
        axv.set_ylabel("Volume", fontsize=9)
        axv.set_xlabel("Time")
        axv.set_yticks([])
        for s in ["top", "right"]:
            axv.spines[s].set_visible(False)
        axv.grid(True, axis="y", color="#1c2230", lw=0.5)

    fig.suptitle("Real Breakout vs. Bull Trap — Volume Confirms", fontsize=14, weight="bold", y=0.97)
    fig.savefig("/home/user/great_files/diagram_2_volume.png", dpi=140, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 3) BEARISH RSI DIVERGENCE
# ---------------------------------------------------------------------------
def rsi_divergence():
    fig, (ax, axr) = plt.subplots(2, 1, figsize=(11, 7),
                                  gridspec_kw={"height_ratios": [3, 1.4], "hspace": 0.12})
    x = np.arange(100)

    # price: two higher highs
    price = (np.sin(x / 9.0) * 4
             + np.linspace(80, 100, 100)
             + np.random.RandomState(5).normal(0, 0.5, 100))
    # force two peaks: peak2 higher than peak1
    price[35] += 4   # first high
    price[80] += 8   # second, higher high
    ax.plot(x, price, color="#e6e6e6", lw=1.7)
    ax.scatter([35, 80], [price[35], price[80]], color=GREEN, s=60, zorder=5)
    ax.plot([35, 80], [price[35], price[80]], color=GREEN, lw=1.5, ls="-")
    ax.text(40, price[35] + 4, "Price: HIGHER high", color=GREEN, fontsize=10, ha="left", weight="bold")
    ax.set_title("Bearish RSI Divergence — the Early Warning", fontsize=14, weight="bold", pad=14)
    ax.set_ylabel("Price")
    ax.set_ylim(78, 112)
    ax.set_xticks([])
    ax.grid(True, color="#1c2230", lw=0.5)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)

    # RSI: two LOWER highs (divergence)
    rsi = 50 + np.sin(x / 9.0) * 18 + np.random.RandomState(6).normal(0, 1.2, 100)
    rsi[35] = 82   # first RSI peak (high)
    rsi[80] = 72   # second RSI peak LOWER -> divergence
    rsi = np.clip(rsi, 5, 95)
    axr.plot(x, rsi, color=BLUE, lw=1.6)
    axr.axhline(70, color=RED, ls="--", lw=1, alpha=0.7)
    axr.axhline(30, color=GREEN, ls="--", lw=1, alpha=0.7)
    axr.text(1, 71, "70 overbought", color=RED, fontsize=8)
    axr.text(1, 24, "30 oversold", color=GREEN, fontsize=8)
    axr.scatter([35, 80], [82, 72], color=RED, s=60, zorder=5)
    axr.plot([35, 80], [82, 72], color=RED, lw=1.5)
    axr.text(57, 86, "RSI: LOWER high", color=RED, fontsize=10, ha="center", weight="bold")
    axr.set_ylabel("RSI (14)")
    axr.set_xlabel("Time")
    axr.set_ylim(0, 100)
    axr.grid(True, color="#1c2230", lw=0.5)
    for s in ["top", "right"]:
        axr.spines[s].set_visible(False)

    # annotation tying it together
    ax.annotate("Price up, momentum down\n→ rally weakening → trap risk",
                xy=(80, price[80]), xytext=(80, price[80] - 16),
                color=AMBER, fontsize=9.5, ha="center",
                arrowprops=dict(arrowstyle="->", color=AMBER))

    fig.savefig("/home/user/great_files/diagram_3_rsi_divergence.png", dpi=140, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    bull_trap_anatomy()
    breakout_vs_trap()
    rsi_divergence()
    print("Saved 3 diagrams.")
