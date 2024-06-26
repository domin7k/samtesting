import argparse
from matplotlib import pyplot as plt
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

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

parser = argparse.ArgumentParser(description="Plot the file sizes and creation times")
parser.add_argument("input", type=str, help="The input file")
args = parser.parse_args()

plt.rcParams.update({"font.family": "serif", "font.serif": []})
plt.rcParams.update({"font.size": 9})


df = pd.read_csv(args.input)
fig, ax = plt.subplots(figsize=(4.804, 3.2))
plt.rcParams.update({"font.family": "serif", "font.serif": []})
plt.rcParams.update({"font.size": 9})


ax2 = ax.twinx()
plt.rcParams.update({"font.family": "serif", "font.serif": []})
plt.rcParams.update({"font.size": 9})


# Plot on ax
cont = ax.bar(
    df["level"], df["size"].to_numpy() / df["size"].to_numpy()[0], color=colorslist
)
plt.bar_label(
    cont,
    fmt="{:.2%}",
    rotation=90,
    fontsize=8,
    label_type="center",
)
ax.set_xticks(range(10))
ax.set_title("File Size after Compression")
ax.set_ylabel("Relative Output Size")
ax.set_xlabel("Compression Level")
ax.set_yticklabels(["{:.0%}".format(x) for x in ax.get_yticks()])


# Plot on ax2
cont2 = ax2.bar(df["level"], df["size"], color=colorslist, alpha=0)
# barlabels = plt.bar_label(
#     cont2,
#     fmt="{:.1f}GiB",
#     fontsize=8,
#     label_type="edge",
#     padding=2,
#     rotation=45,
# )
# barlabels[0].set_rotation(0)
ax2.set_ylabel("Actual Size (GiB)")

plt.tight_layout()

# Make sure ax and ax2 are independent
ax.autoscale(enable=True)
ax2.autoscale(enable=True)
# Plot the actual sizes on the second y-axis
# plt.xticks(range(9))


# Show the plot
# plt.show()

print(df)
fig = plt.figure(figsize=(4.804, 3.8))
ax = fig.add_subplot()

plt.errorbar(
    0,
    -2000,
    yerr=0,
    marker="o",
    fillstyle="none",
    label=f"Level 0",
    capsize=2,
)
median = df.groupby("level").median()
max = df.groupby("level").max()
min = df.groupby("level").min()

for l in range(1, 10):
    plt.errorbar(
        range(5),
        median[["1t", "2t", "4t", "8t", "16t"]].iloc[l],
        yerr=[
            median[["1t", "2t", "4t", "8t", "16t"]].iloc[l]
            - min[["1t", "2t", "4t", "8t", "16t"]].iloc[l],
            max[["1t", "2t", "4t", "8t", "16t"]].iloc[l]
            - median[["1t", "2t", "4t", "8t", "16t"]].iloc[l],
        ],
        marker="o",
        fillstyle="none",
        label=f"Level {l}",
        capsize=2,
    )


plt.legend(ncol=2)
plt.xlabel("Number of Threads")
plt.ylabel("Throughput [MiB/s]")
plt.xticks(range(5), [1, 2, 4, 8, 16])
plt.ylim(bottom=0, top=900)
plt.title("Compression Throughput at Compression Levels")
plt.tight_layout()


inset = inset_axes(ax, width=1.3, height=1, loc=3, bbox_to_anchor=(65, 130))
for l in range(0, 10):
    plt.errorbar(
        range(5),
        median[["1t", "2t", "4t", "8t", "16t"]].iloc[l],
        yerr=[
            median[["1t", "2t", "4t", "8t", "16t"]].iloc[l]
            - min[["1t", "2t", "4t", "8t", "16t"]].iloc[l],
            max[["1t", "2t", "4t", "8t", "16t"]].iloc[l]
            - median[["1t", "2t", "4t", "8t", "16t"]].iloc[l],
        ],
        marker="o",
        fillstyle="none",
        label=f"Level {l}",
        capsize=2,
    )
plt.xticks(range(5), [1, 2, 4, 8, 16])
plt.gca().yaxis.tick_right()

plt.show()
