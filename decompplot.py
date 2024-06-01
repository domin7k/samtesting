from matplotlib import pyplot as plt
import pandas as pd
import re


df = pd.read_csv(
    "/home/dominik/fusessh/2024-05-14T19:47:20.295867decompressionLibdeflate3Times/results.csv"
)
df2 = pd.read_csv(
    "/home/dominik/fusessh/2024-05-14T15:05:49.083200decompressionZlib3times/results.csv"
)

df = df[~df["params"].str.contains("sorted.bam")]
df2 = df2[~df2["params"].str.contains("sorted.bam")]


avg = df.groupby(["params", "branch"], as_index=False)["execution_time"].mean()
avg = avg.sort_values(by=["execution_time"])
std = df.groupby(["params", "branch"], as_index=False)["execution_time"].std()
std = std.sort_values(by=["execution_time"])

avg2 = df2.groupby(["params", "branch"], as_index=False)["execution_time"].mean()
avg2 = avg2.sort_values(by=["execution_time"])
std2 = df2.groupby(["params", "branch"], as_index=False)["execution_time"].std()

fig = plt.figure(figsize=(4.804, 3))
plt.rcParams.update({"font.family": "serif", "font.serif": []})

params = [
    re.sub(r"\d", lambda m: f" ({m.group()})", a.split("sorted")[2].split(".bam")[0])
    for a in avg["params"]
]
params2 = [
    re.sub(r"\d", lambda m: f" ({m.group()})", a.split("sorted")[2].split(".bam")[0])
    for a in avg2["params"]
]

# Sort avg2 and params2 based on the order of params in avg
avg2_sorted = avg2.reindex(avg["params"].index)
std_sorted = std.reindex(avg["params"].index)
std2_sorted = std2.reindex(avg["params"].index)
params2_sorted = [params2[i] for i in avg["params"].index]

plt.hlines(
    avg2["execution_time"].mean(),
    -1,
    len(avg["execution_time"]),
    linestyles="dashed",
    label="avg zlib",
    colors="#009dae",
)
plt.hlines(
    avg["execution_time"].mean(),
    -1,
    len(avg["execution_time"]),
    label="avg libdeflate",
    linestyles="dashed",
    colors="#377eb8",
)

plt.bar(
    [p + 0.2 for p in range(len(params2_sorted))],
    avg2_sorted["execution_time"],
    label="zlib",
    width=0.4,
    color="#009dae",
    # "#e41a1c",
    # "#e41a1c",
    # "#f781bf",
    # "#a65628",
    # "#4daf4a",
    # "#984ea3",
    # "#999999",
    # "#dede00",
    # "#377eb8",
)
plt.errorbar(
    [p + 0.2 for p in range(len(params2_sorted))],
    avg2_sorted["execution_time"],
    yerr=std2_sorted["execution_time"],
    fmt="None",
    ecolor="black",
    capsize=2,
    lw=0.5,
)
plt.bar(
    [p - 0.2 for p in range(len(params))],
    avg["execution_time"],
    label="libdeflate",
    width=0.4,
)
plt.errorbar(
    [p - 0.2 for p in range(len(params))],
    avg["execution_time"],
    yerr=std["execution_time"],
    fmt="None",
    ecolor="black",
    capsize=2,
    lw=0.5,
)


plt.xticks(
    range(len(params)),
    [p if p != "uncomp" else "uncompressed" for p in params],
    rotation=35,
    ha="right",
    rotation_mode="anchor",
)


plt.title("Decompression Performance")
plt.ylabel("Execution Time [s]")
plt.legend(loc="lower right", ncol=2)
plt.tight_layout()

plt.show()


# -rw-r--r--. 1 extsiebe PEONS  30G May  4 23:24 sortedigzip1.bam
# -rw-r--r--. 1 extsiebe PEONS  22G May  4 23:28 sortedigzip3.bam
# -rw-r--r--. 1 extsiebe PEONS  22G May  4 23:06 sortedlibdeflate1.bam
# -rw-r--r--. 1 extsiebe PEONS  20G May  4 23:11 sortedlibdeflate6.bam
# -rw-r--r--. 1 extsiebe PEONS  25G May  4 22:51 sortedminiz1.bam
# -rw-r--r--. 1 extsiebe PEONS  20G May  4 22:57 sortedminiz6.bam
# -rw-r--r--. 1 extsiebe PEONS  29G May  4 23:02 sortedslz1.bam
# -rw-r--r--. 1 extsiebe PEONS 104G May  5 00:27 sorteduncomp.bam
# -rw-r--r--. 1 extsiebe PEONS  24G May  4 13:38 sortedzlib1.bam
# -rw-r--r--. 1 extsiebe PEONS  20G May  4 13:44 sortedzlib6.bam
# -rw-r--r--. 1 extsiebe PEONS  29G May  4 23:15 sortedzlibng1.bam
# -rw-r--r--. 1 extsiebe PEONS  19G May  4 23:20 sortedzlibng6.bam
# -rw-r--r--. 1 extsiebe PEONS  18G May  4 17:14 sortedzopfli1.bam
# -rw-r--r--. 1 extsiebe PEONS  18G May  4 22:47 sortedzopfli6.bam
