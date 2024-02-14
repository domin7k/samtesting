import json
import matplotlib.pyplot as plt


# add command line argument for input file
import argparse

import numpy as np

from helpers.formating import HumanBytes

parser = argparse.ArgumentParser(description="Plot the file sizes and creation times")
parser.add_argument("input", type=str, help="The input file")
args = parser.parse_args()


# Load the JSON data
with open(args.input) as f:
    data = json.load(f)


# Separate the file sizes into two lists: tmp_files and other_files
# Prepare the event plot data
lines = []
legendLabels = []
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
all_color = []
all_size = []
max_time_span = 0
legendColors = []
ticks = []
ticks_idx = []
sizes_human_readable = []
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

    plt.bar(
        all_ticks,
        sorted_sizes,
        label=all_lines[0][0][i][4],
        bottom=all_xs,
    )
    all_xs += sorted_sizes


# Add legend to the plot
plt.legend()

# Show the plot
plt.show()
