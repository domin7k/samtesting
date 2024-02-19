import json
import matplotlib.pyplot as plt


# add command line argument for input file
import argparse

import numpy as np
import pandas as pd

from helpers.formating import HumanBytes

parser = argparse.ArgumentParser(description="Plot the file sizes and creation times")
parser.add_argument("input", type=str, help="The input file")
args = parser.parse_args()


df = pd.read_csv(args.input)

avgs = df.groupby(["branch", "params", "file"], as_index=False).mean()
stds = df.groupby(["branch", "params", "file"], as_index=False).std(ddof=0)
print(avgs)
params = avgs[["branch", "params"]].drop_duplicates()
print(params)
for idx, (file, file_data) in enumerate(data.items()):
    for i, (process, process_data) in enumerate(file_data.items()):
        creation_time = process_data["creation_time"]
        last_modified = process_data["last_modified"]
        size = process_data["size"]
        deleted = process_data["deleted"]
        if i >= len(lines):
            lines.append([])
        lines[i].append([creation_time, last_modified, size, deleted, file])
        if process.split("-o")[0].strip() not in legendLabels:
            legendLabels.append(process.split("-o")[0].strip())

print(legendLabels)

# colors = iter(cm.tab20b(np.linspace(0, 1, len(lines))))

all_ticks = []
all_xs = np.zeros(2 * 2)

all_lines = []
for i, process in enumerate(lines):
    process_tmp = [line for line in process if "tmp" in line[4]]
    process_other = [line for line in process if "tmp" not in line[4]]
    all_lines.append([process_tmp, process_other])

max_tmp = max(max([len(line[0]) for line in all_lines]), 1)
for i in range(len(legendLabels)):
    all_ticks.append(legendLabels[i] + " tmp")
    all_ticks.append(legendLabels[i])

for line in all_lines:
    while len(line[0]) < max_tmp:
        line[0].append([0, 0, 0, 0, ""])
    while len(line[1]) < max_tmp:
        line[1].append([0, 0, 0, 0, ""])

print(len(all_ticks))
print(
    len(
        [line[0][0][2] for line in all_lines] + [line[1][0][2] for line in all_lines],
    )
)
process_with_tmp = 0

patches = []
for i in range(max_tmp):

    label = all_lines[process_with_tmp][0][i][4]
    while label == "":
        process_with_tmp += 1
        label = all_lines[process_with_tmp][0][i][4]

    sorted_sizes = [
        x
        for y in zip(
            [line[0][i][2] for line in all_lines],
            [line[1][i][2] for line in all_lines],
        )
        for x in y
    ]

    patches.extend(
        plt.bar(
            all_ticks,
            sorted_sizes,
            label=all_lines[0][0][i][4],
            bottom=all_xs,
            width=0.5,
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
        HumanBytes.format(all_xs[i]) if all_xs[i] > 0 else "",
        ha="center",
        va="bottom",
        weight="bold",
        color="k",
        size=8,
    )


# Add legend to the plot
plt.legend()

# Show the plot
plt.show()
