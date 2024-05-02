from matplotlib import pyplot as plt
import pandas as pd

colorslist = [
    "#377eb8",
    "#ff7f00",
    "#e41a1c",
    "#f781bf",
    "#a65628",
    "#4daf4a",
    "#984ea3",
    "#999999",
    "#dede00",
    "#377eb8",
]


df = pd.read_csv("/home/dominik/ba/compressionComparison.csv")
fig, ax = plt.subplots(figsize=(4.804, 3))
plt.rcParams.update({"font.family": "serif", "font.serif": []})

plt.rcParams.update({"font.family": "serif", "font.serif": []})

df = df.sort_values("size", ascending=False)
# Plot on ax
cont = ax.bar(
    df["method"].to_numpy()[1:],
    df["size"].to_numpy()[1:] / df["size"].to_numpy()[0],
    # color=colorslist,
)
plt.bar_label(
    cont,
    fmt="{:.2%}",
    rotation=90,
    fontsize=8,
    label_type="center",
)
ax.set_xticks(
    range(13), df["method"][1:], rotation=30, ha="right", rotation_mode="anchor"
)
ax.set_title("Compression Ratios of GZIP Implementations")
ax.set_ylabel("Output Size \n relative to Uncompressed")
ax.set_xlabel("Implementation (Level)")
# use percentage for y-axis
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: "{:.0%}".format(x)))

plt.tight_layout()

plt.show()
