from matplotlib import cm
import matplotlib.pyplot as plt
import json
import numpy as np
import pandas as pd
from helpers.formating import HumanBytes

# add command line argument for input file
import argparse

parser = argparse.ArgumentParser(description="Plot the file sizes and creation times")
parser.add_argument("input", type=str, help="The input file")
args = parser.parse_args()

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
# # Load the JSON data
# with open(args.input) as f:
#     data = json.load(f)

# # Prepare the event plot data
# lines = []
# legendLabels = []
# for idx, (file, file_data) in enumerate(data.items()):
#     for i, (process, process_data) in enumerate(file_data.items()):
#         creation_time = process_data["creation_time"]
#         last_modified = process_data["last_modified"]
#         size = process_data["size"]
#         deleted = process_data["deleted"]
#         if i >= len(lines):
#             lines.append([])
#         lines[i].append([creation_time, last_modified, size, deleted, file])
#         legendLabels.append(process.split("-o")[0].strip())

# print(len(legendLabels))
# colors = iter(cm.tab20b(np.linspace(0, 1, len(lines))))

df = pd.read_csv(args.input)
df = df[
    df["params"]
    == "sort -@ 1 -m 400M -o ../sorted/outputOfTest_3/sorted.bam ../unsorted_bam_files/onepercent.bam"
]

max_run_counter = df["run_counter"].max()
middle = int(max_run_counter / 2) if max_run_counter > 1 else 0
print(
    f"drawing run with the {middle}th highest execution time of {max_run_counter} runs"
)

# Group the DataFrame by 'run_counter', 'branch', and 'params' and get the 'timestamp' value
df["start"] = df.groupby(["run_counter", "branch", "params"])["timestamp"].transform(
    "first"
)
df["from_start"] = df["timestamp"] - df["start"]
# print(df)
idx = df.groupby(["run_counter", "branch", "params"])["from_start"].idxmax()
rows_with_max_from_start = df.loc[idx]


most_average_runs_per_param = rows_with_max_from_start.groupby(
    ["branch", "params"]
).apply(lambda x: x.nlargest(middle + 1, "from_start").iloc[-1])
most_average_runs_per_param.reset_index(inplace=True, drop=True)


avg_only = pd.merge(
    df,
    most_average_runs_per_param[["run_counter", "branch", "params"]],
    on=["run_counter", "branch", "params"],
    how="inner",
)


lines = {}  # Initialize the lines dictionary
events = {}
for n, group in avg_only.groupby(["branch", "params"]):
    name = n[0] + " " + n[1]
    if name not in lines:
        lines[name] = {}
        events[name] = []
    for _, row in group.iterrows():
        if row["file"] == "any":
            events[name].append((row["operation"], row["from_start"]))
        else:
            if row["file"] not in lines[name]:
                lines[name][row["file"]] = {}

            lines[name][row["file"]][row["operation"]] = row["from_start"]


all_ys = []
all_xs = []
all_color = []
all_size = []
max_dur = 0
legendColors = []
legendLabels = []
ticks = []
ticks_idx = []
sizes_human_readable = []
for i, (process, files) in enumerate(
    sorted(
        lines.items(),
        key=lambda p: (
            int(p[0].strip().split(" -@ ")[1].strip().split(" ")[0])
            if " -@ " in p[0]
            else p[0]
        ),
    )
):
    max_time = max([x[1] for x in events[process]])
    max_dur = max(max_dur, max_time)

    for _, file in files.items():
        if "deleted" not in file:
            file["deleted"] = max_time

    color = colorslist[i]

    active_ys = range(
        i, len(files.items()) * (len(lines.items()) + 1), len(lines.items()) + 1
    )
    active_xs = [
        [
            file["writestart"],
            file["mergeend"] if "mergeend" in file else file["writeend"],
        ]
        for _, file in files.items()
    ]
    active_color = [color for _ in files.items()]
    active_size = [3 for _ in files.items()]
    a_ticks = [n for n, _ in files.items()]
    # a_sizes = [HumanBytes.format(line[2]) for line in process]

    ondisk_xs = [
        [
            file["mergeend"] if "mergeend" in file else file["writeend"],
            (file["deleted"] if file["deleted"] > 0 else max_time),
        ]
        for _, file in files.items()
    ]
    ondisk_color = ["k" for _ in files.items()]
    inactive_size = [1 for _ in files.items()]

    all_ys = all_ys + list(active_ys) + list(active_ys)
    all_xs = all_xs + active_xs + ondisk_xs
    all_color = all_color + active_color + ondisk_color
    all_size = all_size + active_size + inactive_size
    ticks_idx = ticks_idx + list(active_ys)
    # sizes_human_readable = (
    #     sizes_human_readable + a_sizes + a_sizes
    # )  # two times to keep length consistent
    ticks = ticks + a_ticks
    legendColors.append(color)
    legendLabels.append(process)

plt.figure()

for y, xs, c, s in zip(all_ys, all_xs, all_color, all_size):
    plt.plot(
        xs,
        [y, y],
        color=c,
        lw=s,
    )
    if type(c) != str:  # filter inactive
        plt.plot(
            xs,
            [y, y],
            lw=1,
            color=c,
        )

add_yticks = []
add_ytickidx = []
for y, (process, sortlist) in enumerate(
    sorted(
        events.items(),
        key=lambda p: (
            int(p[0].strip().split(" -@ ")[1].strip().split(" ")[0])
            if " -@ " in p[0]
            else p[0]
        ),
    )
):
    ys = y - len(legendLabels) - 2
    add_ytickidx.append(ys)
    add_yticks.append("Sorting Activity")

    ordered_list = sorted(sortlist, key=lambda x: x[1])
    print(ordered_list)
    sort = [0, 0]
    time_list = []
    start = 0
    end = 0
    for op, time in ordered_list:
        if op == "start":
            start = time
        if op == "end":
            end = time
        if op == "sortstart":
            sort[0] = time
        elif op == "sortend":
            sort[1] = time
            time_list.append(sort)
            sort = [0, 0]
    print(time_list)

    c = legendColors[y]
    plt.plot([start, end], [ys, ys], linestyle="--", color=c, lw=1),

    for xs in time_list:
        plt.plot(
            xs,
            [ys, ys],
            color=c,
            lw=3,
        )
        plt.axvline(x=xs[0], color=c, linestyle="--", lw=0.5)
        plt.axvline(x=xs[1], color=c, linestyle="--", lw=0.5)
# for x in [a[1] for a in all_xs]:
#     plt.axvline(x=x, color="gray", linestyle="--", lw=0.5)
# for x in [a[1] for a in all_xs]:
#     plt.axvline(x=x, color="gray", linestyle="--", lw=0.5)


print(f"legend colors length: {len(legendColors)}")

plt.xticks(fontsize=12)
plt.yticks(add_ytickidx + ticks_idx, add_yticks + ticks, fontsize=8)
plt.xlim(0, max_dur)
plt.ylim(len(lines.items()) * -1.5, max(all_ys) + 1)
plt.xlabel("time (s)", fontsize=12)
plt.ylabel("Files", fontsize=12)

plt.legend(
    handles=[
        plt.Line2D(
            [0], [0], linewidth=3, color=c, label=legendLabels[process].split(" -o")[0]
        )
        for process, c in enumerate(legendColors)
    ]
    + [
        plt.Line2D(
            [0], [0], linewidth=1, color="k", label="file not modified but on disk"
        )
    ],
    bbox_to_anchor=(0.0, 1.02, 1.0, 0.102),
    loc="lower left",
    mode="expand",
    borderaxespad=0.0,
)
plt.show()
