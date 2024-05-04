from matplotlib import pyplot as plt
import pandas as pd


df = pd.read_csv(
    "/home/dominik/fusessh/2024-05-04T13:24:56.134789decompSingleCoreLibdeflate/results.csv"
)

df = df[~df["params"].str.contains("sorted.bam")]


avg = df.groupby(["params", "branch"], as_index=False)["execution_time"].mean()
avg = avg.sort_values(by=["execution_time"])

plt.bar(
    [a.split("sorted")[2].split(".bam")[0] for a in avg["params"]],
    avg["execution_time"],
)
plt.xticks(rotation=35, ha="right")

plt.hlines(
    avg[~avg["params"].str.contains("uncomp")]["execution_time"].mean(),
    -1,
    len(avg["execution_time"]),
    colors="r",
)
plt.text(
    -1,
    avg[~avg["params"].str.contains("uncomp")]["execution_time"].mean() * 1.01,
    "Average of compressed files",
    color="r",
)

plt.show()
