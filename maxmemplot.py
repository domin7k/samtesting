import argparse
import subprocess
import sys
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker


PARAM = "-l"

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


# ArgumentParser erstellen und Argument hinzufügen
parser = argparse.ArgumentParser(description="Plot.")
parser.add_argument(
    "-d",
    dest="desciption2",
    type=str,
    help="The description of the second csv file.",
    default=None,
    nargs="*",
    action="append",
)
# optionales zweites argument für zweites input csv
parser.add_argument(
    "-f",
    dest="filename2",
    type=str,
    help="The filename to get the csv data from.",
    default=None,
    nargs="*",
    action="append",
)
parser.add_argument(
    "-p",
    dest="param",
    type=str,
    help="the param to plot against",
    default=PARAM,
    nargs="?",
)

parser.add_argument(
    "-pname",
    dest="paramname",
    type=str,
    help="the param display name to plot against",
    default=PARAM,
    nargs="?",
)

parser.add_argument(
    "-save",
    "-safe",
    dest="save",
    type=str,
    help="name of the plot file to save",
    nargs="?",
)

parser.add_argument(
    "-title", dest="title", type=str, help="title of the plot", nargs="?"
)

parser.add_argument(
    "-yaxis",
    dest="yaxis",
    type=str,
    help="title of the yaxis",
    default="Execution Time [s]",
)

parser.add_argument(
    "-time",
    dest="time",
    type=str,
    default="execution_time",
    help="time to plot",
)

# add argument to indicate if speedup should be plotted
parser.add_argument(
    "-s",
    dest="speedup",
    action="store_true",
    help="plot the speedup instead of the execution time",
)


args = parser.parse_args()

param = args.param


def extractParam(param_string):
    if type(param_string) is not str:
        return "No Param"
    return param_string.strip().split(param)[1].strip().split(" ")[0]


df_avgs = []
df_mins = []
df_maxs = []
plt.figure(figsize=(4.804, 3))
plt.rcParams.update({"font.family": "serif", "font.serif": []})
plt.rcParams.update({"font.size": 9})

print(args.filename2)
print(args.desciption2)
# Read the CSV file
for no, file in enumerate([item for row in args.filename2 for item in row]):
    if not file:
        continue

    df = pd.read_csv(file)

    avg = df.groupby(["params", "branch"], as_index=False)[args.time].mean()

    df_min = df.groupby(["params", "branch"], as_index=False)[args.time].min()
    df_max = df.groupby(["params", "branch"], as_index=False)[args.time].max()
    print(avg)

    avg[param] = avg["params"].apply(extractParam)
    df_max[param] = df_max["params"].apply(extractParam)
    df_min[param] = df_min["params"].apply(extractParam)

    avg[param] = avg[param].apply(
        lambda x: (
            x if not (x.endswith("M") or x.endswith("G")) else x.strip("M").strip("G")
        )
    )
    df_max[param] = df_max[param].apply(
        lambda x: (
            x if not (x.endswith("M") or x.endswith("G")) else x.strip("M").strip("G")
        )
    )
    df_min[param] = df_min[param].apply(
        lambda x: (
            x if not (x.endswith("M") or x.endswith("G")) else x.strip("M").strip("G")
        )
    )

    avg[param] = avg[param].apply(pd.to_numeric, errors="coerce")
    df_max[param] = df_max[param].apply(pd.to_numeric, errors="coerce")
    df_min[param] = df_min[param].apply(pd.to_numeric, errors="coerce")

    avg = avg.sort_values(by=[param])
    df_max = df_max.sort_values(by=[param])
    df_min = df_min.sort_values(by=[param])

    if not args.speedup:
        plt.errorbar(
            range(len(avg[args.time])),
            avg[args.time].to_numpy(),
            yerr=[
                avg[args.time].to_numpy() - df_min[args.time].to_numpy(),
                df_max[args.time].to_numpy() - avg[args.time].to_numpy(),
            ],
            marker="o",
            fillstyle="none",
            color=colorslist[no],
            label=((args.desciption2[no][0]) if args.desciption2 else None),
            capsize=2,
        )
    else:
        df_mins.append(df_min)
        df_maxs.append(df_max)
        df_avgs.append(avg)

speedup_values = []
if args.speedup:
    plt.gca().axhline(1, linestyle="--", color="r", linewidth=0.5)
    for numberofdf, df_avg in enumerate(df_avgs):
        speedup_values = df_avgs[0][args.time].to_numpy() / df_avg[args.time].to_numpy()
        speedup_max = (
            df_avgs[0][args.time].to_numpy() / df_mins[numberofdf][args.time].to_numpy()
        )
        speedup_min = (
            df_avgs[0][args.time].to_numpy() / df_maxs[numberofdf][args.time].to_numpy()
        )
        # plt.plot(
        #     range(len(df_avgs[0][args.time])),
        #     speedup_values,
        #     # marker="o",
        #     fillstyle="none",
        #     label=(args.desciption2[numberofdf][0].replace("\\n", "\n")),
        # )
        plt.errorbar(
            range(len(df_avg[args.time])),
            speedup_values,
            yerr=[speedup_values - speedup_min, speedup_max - speedup_values],
            marker="o",
            fillstyle="none",
            color=colorslist[numberofdf],
            label=(args.desciption2[numberofdf][0].replace("\\n", "\n")),
            capsize=2,
        )


# Add labels and title
plt.xlabel(args.paramname if args.paramname else param)
plt.ylim(bottom=0)

if not args.speedup:
    plt.ylabel(args.yaxis)
    plt.title(
        args.title
        if args.title
        else f"Execution Time vs {args.paramname if args.paramname else param}"
    )
else:
    plt.ylabel("Speedup \n ")
    plt.title(
        args.title
        if args.title
        else f"Speedup vs {args.paramname if args.paramname else param}"
    )
    # format y ticks
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:.1f}"))

    # set yticks to percent
    # plt.gca().yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))
    # for i, v in enumerate(speedup_values):
    #     plt.annotate(
    #         f"{v:.2%}",
    #         xy=(i, v),
    #         xytext=(0, -7),
    #         textcoords="offset points",
    #         ha="center",
    #         va="top",
    #     )


# Set xticks
plt.xticks(range(len(avg[args.time])), avg[param], rotation=45)
plt.ylim(top=500 if not args.speedup else 2)


if args.desciption2:
    plt.legend()
plt.tight_layout()

if args.save:
    plt.savefig(
        "../Faster-Sorting-of-Aligned-DNA-Reads-Files/figures/" + args.save + ".pgf",
        bbox_inches="tight",
    )
    with open(
        "../Faster-Sorting-of-Aligned-DNA-Reads-Files/figures/" + args.save + ".txt",
        "w",
    ) as f:
        cmd = " ".join(
            [sys.argv[0]]
            + [
                s if s.startswith("-") and not " " in s else '"' + s + '"'
                for s in sys.argv[1:]
            ]
        )
        f.write(cmd)
    subprocess.run(
        f"(cd ../Faster-Sorting-of-Aligned-DNA-Reads-Files/figures/ && git pull && git add . && git commit -m 'added plot {args.save}' && git push)",
        shell=True,
    )


# Show the plot
plt.show()
