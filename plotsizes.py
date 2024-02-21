import json
import os
import matplotlib.pyplot as plt


# add command line argument for input file
import argparse

import numpy as np
import pandas as pd

from helpers.formating import HumanBytes

colorslist = [
    "#377eb8",
    "#ff7f00",
    "#e41a1c",
    "#f781bf",
    "#a65628",
    "#4daf4a",
    "#984ea3",
    "#dede00",
]
sortedcolor = "#999999"

parser = argparse.ArgumentParser(description="Plot the file sizes and creation times")
parser.add_argument("input", type=str, help="The input file")
args = parser.parse_args()


df = pd.read_csv(args.input)

avgs = df.groupby(["branch", "params", "file"], as_index=False).mean()
stds = df.groupby(["branch", "params", "file"], as_index=False).std(ddof=0)
print(avgs)
params = avgs[["branch", "params"]].drop_duplicates()
print(params)

all_ticks = []
all_xs = np.zeros(2 * 2)

all_lines = []
stdslist = []
legendLabels = []
for idx, param in params.iterrows():
    avgsgen = avgs[
        (avgs["branch"] == param["branch"]) & (avgs["params"] == param["params"])
    ]
    stdsgen = stds[
        (stds["branch"] == param["branch"])
        & (stds["params"] == param["params"])
        & (stds["file"] == stds["file"])
    ]
    process_tmp = [
        [os.path.basename(file["file"]), file["branch"], file["params"], file["bytes"]]
        for _, file in avgsgen.iterrows()
        if "tmp" in file["file"]
    ]
    process_other = [
        [os.path.basename(file["file"]), file["branch"], file["params"], file["bytes"]]
        for _, file in avgsgen.iterrows()
        if "tmp" not in file["file"]
    ]
    std_process_tmp = [
        file["bytes"] for _, file in stdsgen.iterrows() if "tmp" in file["file"]
    ]
    std_process_other = [
        file["bytes"] for _, file in stdsgen.iterrows() if "tmp" not in file["file"]
    ]
    all_lines.append([process_tmp, process_other])
    stdslist.append([std_process_tmp, std_process_other])
    legendLabels.append(param["branch"] + "\n" + param["params"])

print(all_lines)

max_tmp = max(max([len(line[0]) for line in all_lines]), 0)
if max_tmp == 0:
    print("ERROR: No temporary files found :(")

for i in range(len(legendLabels)):
    all_ticks.append(legendLabels[i].strip().split(" -o")[0] + " tmp")
    all_ticks.append(legendLabels[i].strip().split(" -o")[0])

for line in all_lines:
    while len(line[0]) < max_tmp:
        line[0].append(["", "", "", 0])
    while len(line[1]) < max_tmp:
        line[1].append(["", "", "", 0])


process_with_tmp = 0

patches = []
all_xs = np.zeros(len(legendLabels) * 2)
for i in range(max_tmp):

    label = all_lines[process_with_tmp][0][i][0]
    while label == "":
        process_with_tmp += 1
        label = all_lines[process_with_tmp][0][i][0]

    sorted_sizes = [
        x
        for y in zip(
            [line[0][i][3] for line in all_lines],
            [line[1][i][3] for line in all_lines],
        )
        for x in y
    ]

    patches.extend(
        plt.bar(
            all_ticks,
            sorted_sizes,
            label=label,
            bottom=all_xs,
            width=0.5,
            color=[
                sortedcolor if a % 2 == 1 else colorslist[i % len(colorslist)]
                for a in range(len(all_ticks))
            ],
        ).patches
    )
    all_xs += sorted_sizes

for bar in patches:
    plt.text(
        # Put the text in the middle of each bar. get_x returns the start
        # so we add half the width to get to the middle.
        bar.get_x() + bar.get_width() / 2,
        # Vertically, add the height of the bar to the start of the bar,
        # along with the offset.
        bar.get_height() / 2 + bar.get_y(),
        # This is actual value we'll show.
        HumanBytes.format(bar.get_height()) if bar.get_height() > 0 else "",
        # Center the labels and style them a bit.
        ha="center",
        va="center",
        color="w",
        size=8,
    )

for i in range(len(all_ticks)):
    plt.text(
        i,
        all_xs[i] + max(all_xs) * 0.005,
        (
            (
                HumanBytes.format(all_xs[i])
                + "\n"
                + "$"
                + ("\sum " if len(stdslist[i // 2][i % 2]) > 1 else "")
                + "\sigma ="
                + str(sum(stdslist[i // 2][i % 2]))
                + "$"
            )
            if all_xs[i] > 0
            else ""
        ),
        ha="center",
        va="bottom",
        weight="bold",
        color="k",
        size=8,
    )
    # plt.text(
    #     i,
    #     all_xs[i] + max(all_xs) * 0.005,
    #     stdslist[i // 2][i % 2],
    #     ha="center",
    #     va="bottom",
    #     weight="bold",
    #     color="grey",
    #     size=8,
    # )


# Add legend to the plot
plt.legend()
plt.ylim((0, max(all_xs) * 1.1))

# Show the plot
plt.show()
