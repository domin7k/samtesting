from matplotlib import pyplot as plt
import pandas as pd
import re

plt.rcParams.update({"font.family": "CMU Serif"})
plt.rcParams.update({"font.size": 9})
plt.rcParams.update({"hatch.color": "white"})

fig, axs = plt.subplots(
    5,
    2,
    figsize=(4.804, 6.5),
    gridspec_kw={
        "hspace": 0.3,
        "wspace": 0.25,
        "top": 0.95,
        "bottom": 0.05,
        "left": 0.1,
        "right": 0.95,
    },
)

fig.text(0.5, 0.001, "Number of Threads", ha="center")
fig.text(0.001, 0.5, "Proportional Time", va="center", rotation="vertical")

directories = [
    "2024-05-09T09:41:50.963904igzip3smallFile",
    "2024-05-09T09:36:10.255986igzip1smallFile",
    "2024-05-09T09:22:43.176437zlibng6smallFile",
    "2024-05-09T09:16:06.136823zlibng1smallFile",
    "2024-05-09T09:05:26.612685libdeflate6smallFile",
    "2024-05-09T08:58:22.466887libdeflate1smallFile",
    "2024-05-09T08:52:15.061057slz1smallFile",
    "2024-05-09T07:50:30.843457zlib6smallFile",
    "2024-05-09T07:39:07.209388zlib1smallFile",
]

dirs = {}
for i, directory in enumerate(directories):
    df = pd.read_csv(f"/home/dominik/fusessh/{directory}/fileinfo.csv")
    df = df[df["run_counter"] == 0]
    times_dict = {}
    for params in df["params"].unique():
        df_params = df[df["params"] == params]
        start = 0
        sortstart = 0
        sortend = 0
        end = 0
        for row in df_params.iterrows():
            row = row[1]
            if row["operation"] == "start":
                start = row["timestamp"]
            elif row["operation"] == "sortstart":
                sortstart = row["timestamp"]
            elif row["operation"] == "sortend":
                sortend = row["timestamp"]
            elif row["operation"] == "end":
                end = row["timestamp"]
        if directory not in dirs:
            dirs[directory] = end - start


for i, directory in enumerate(sorted(directories, key=lambda x: dirs[x])):
    df = pd.read_csv(f"/home/dominik/fusessh/{directory}/fileinfo.csv")
    df = df[df["run_counter"] == 1]
    times_dict = {}
    for params in df["params"].unique():
        df_params = df[df["params"] == params]
        start = 0
        sortstart = 0
        sortend = 0
        end = 0
        for row in df_params.iterrows():
            row = row[1]
            if row["operation"] == "start":
                start = row["timestamp"]
            elif row["operation"] == "sortstart":
                sortstart = row["timestamp"]
            elif row["operation"] == "sortend":
                sortend = row["timestamp"]
            elif row["operation"] == "end":
                end = row["timestamp"]
        relative_decompression_time = (sortstart - start) / (end - start)
        relative_sorting_time = (sortend - sortstart) / (end - start)
        relative_compression_time = (end - sortend) / (end - start)
        times_dict[params] = {
            "start": start,
            "sortstart": sortstart,
            "sortend": sortend,
            "end": end,
            "total_time": end - start,
            "decompression_time": sortstart - start,
            "sorting_time": sortend - sortstart,
            "compression_time": end - sortend,
            "relative_decompression_time": relative_decompression_time,
            "relative_sorting_time": relative_sorting_time,
            "relative_compression_time": relative_compression_time,
        }
        print(times_dict[params])
    ax = axs[i // 2, i % 2]
    ax.fill_between(
        range(len(times_dict)),
        0,
        [times_dict[param]["relative_decompression_time"] for param in times_dict],
        fc="#377eb8",
        hatch="\\\\\\",
        label="Decompression Time",
    )
    ax.fill_between(
        range(len(times_dict)),
        [times_dict[param]["relative_decompression_time"] for param in times_dict],
        [
            times_dict[param]["relative_decompression_time"]
            + times_dict[param]["relative_sorting_time"]
            for param in times_dict
        ],
        fc="#ff7f00",
        hatch="+++",
        label="Sorting Time",
    )
    ax.plot(
        range(len(times_dict)),
        [
            times_dict[param]["relative_decompression_time"]
            + times_dict[param]["relative_sorting_time"]
            for param in times_dict
        ],
        marker="x",
        lw=0,
        color="black",
        markersize=3,
    )
    ax.plot(
        range(len(times_dict)),
        [times_dict[param]["relative_decompression_time"] for param in times_dict],
        marker="x",
        lw=0,
        color="black",
        markersize=3,
    )
    ax.fill_between(
        range(len(times_dict)),
        [
            times_dict[param]["relative_decompression_time"]
            + times_dict[param]["relative_sorting_time"]
            for param in times_dict
        ],
        [
            times_dict[param]["relative_decompression_time"]
            + times_dict[param]["relative_sorting_time"]
            + times_dict[param]["relative_compression_time"]
            for param in times_dict
        ],
        fc="#e41a1c",
        hatch="///",
        label="Compression Time",
    )
    ax.set_xticks(range(len(times_dict)))
    ax.set_xticklabels(
        [
            param.strip().split("@")[1].strip().split(" ")[0]
            for param in times_dict.keys()
        ],
    )
    # ax.set_yticklabels(["{:.0f}%".format(x * 100) for x in ax.get_yticks()])
    directory_name = re.sub(
        r"[^a-zA-Z]+", "", directory.split("T")[1].split("smallFile")[0]
    )
    number = re.findall(r"\d+", directory)[-1]
    directory_name = directory_name + f" ({number})"
    # ax.set_title(directory_name, y=1.0, pad=-20)
    ax.legend([], [], title=directory_name, loc="upper center")

# plot a legend with the same colors as the plot
axs[4, 1].fill_between(
    [], [], hatch="///", fc="#e41a1c", label="Compression", alpha=0.99
)
axs[4, 1].fill_between([], [], hatch="+++", fc="#ff7f00", label="Sorting")
axs[4, 1].fill_between([], [], hatch="\\\\\\", fc="#377eb8", label="Decompression")


axs[4, 1].legend(loc="lower right")
axs[4, 1].axis("off")

fig.suptitle("Proportional Time for Decompression, Sorting, and Compression")

plt.show()
