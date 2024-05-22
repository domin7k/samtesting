import argparse
import subprocess
import sys
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker

from helpers.formating import HumanBytes


PARAM = "unsorted_bam_files/"

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
    default="Execution Time [m]",
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

# add argument to indicate if speedup should be plotted
parser.add_argument(
    "-r",
    dest="relative",
    action="store_true",
    help="plot the speedup to first core",
)

parser.add_argument(
    "-yheight", dest="hight", default=4.0, type=float, help="hight of the plot"
)

parser.add_argument(
    "-ylim", dest="ylim", default=0, type=float, help="ylim of the plot"
)

parser.add_argument("-ncols", dest="ncols", default=1, type=int, help="ncols of legend")


args = parser.parse_args()

param = args.param
if len([item for row in args.filename2 for item in row]) > 10:
    colorslist = matplotlib.cm.tab20.colors


def extractParam(param_string):
    if type(param_string) is not str:
        return "No Param"
    return param_string.strip().split(param)[1].strip().split(" ")[0]


df_avgs = []
df_mins = []
df_maxs = []
plt.figure(figsize=(4.804, args.hight))
plt.rcParams.update({"font.family": "serif", "font.serif": []})
plt.rcParams.update({"font.size": 9})
max_values = []

print(args.filename2)
print(args.desciption2)
# Read the CSV file
for no, file in enumerate([item for row in args.filename2 for item in row]):
    if not file:
        continue

    df = pd.read_csv(file)

    median = df.groupby(["params", "branch"], as_index=False)[args.time].median()

    df_min = df.groupby(["params", "branch"], as_index=False)[args.time].min()
    df_max = df.groupby(["params", "branch"], as_index=False)[args.time].max()
    df_stf = df.groupby(["params", "branch"], as_index=False)[args.time].std()

    median[param] = median["params"].apply(extractParam)
    df_max[param] = df_max["params"].apply(extractParam)
    df_min[param] = df_min["params"].apply(extractParam)
    df_stf[param] = df_stf["params"].apply(extractParam)

    def replacePercentages(input_string):
        print(input_string)
        sizeList = [
            2430911988,
            11915810774,
            23610152212,
            115885627243,
            230919299324,
        ]
        for i, find in enumerate(
            [
                "onepercent.bam",
                "fivepercent.bam",
                "tenpercent.bam",
                "fiftypercent.bam",
                "ocopy.bam",
            ]
        ):
            if find in input_string:
                print(f"Found {find} in {input_string}")
                return sizeList[i]
        return input_string

    median[param] = median[param].apply(lambda x: replacePercentages(x))
    df_max[param] = df_max[param].apply(lambda x: replacePercentages(x))
    df_min[param] = df_min[param].apply(lambda x: replacePercentages(x))
    df_stf[param] = df_stf[param].apply(lambda x: replacePercentages(x))

    median[param] = median[param].apply(pd.to_numeric, errors="coerce")
    df_max[param] = df_max[param].apply(pd.to_numeric, errors="coerce")
    df_min[param] = df_min[param].apply(pd.to_numeric, errors="coerce")
    df_stf[param] = df_stf[param].apply(pd.to_numeric, errors="coerce")

    median = median.sort_values(by=[param])
    df_max = df_max.sort_values(by=[param])
    df_min = df_min.sort_values(by=[param])
    df_stf = df_stf.sort_values(by=[param])

    max_values.append([median[args.time][0], no])

    print(median)

    if not args.speedup and not args.relative:
        # if not df_min.equals(df_max):
        #     # Plot the execution time against the 'mem' column
        #     plt.fill_between(
        #         x=range(len(avg[args.time])),
        #         y1=df_min[args.time].to_numpy(),
        #         y2=df_max[args.time].to_numpy(),
        #         alpha=0.20,
        #         color=colorslist[no],
        #     )

        #     plt.plot(
        #         range(len(avg[args.time])),
        #         df_max[args.time].to_numpy(),
        #         marker=7,
        #         fillstyle="none",
        #         lw=0,
        #         color=colorslist[no],
        #     )
        #     plt.plot(
        #         range(len(avg[args.time])),
        #         df_min[args.time].to_numpy(),
        #         marker=6,
        #         fillstyle="none",
        #         lw=0,
        #         color=colorslist[no],
        #     )
        plt.errorbar(
            median[param].to_numpy(),
            median[args.time].to_numpy(),
            yerr=[
                median[args.time].to_numpy() - df_min[args.time].to_numpy(),
                df_max[args.time].to_numpy() - median[args.time].to_numpy(),
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
        df_avgs.append(median)

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
            df_avg[param].to_numpy(),
            speedup_values,
            yerr=[speedup_values - speedup_min, speedup_max - speedup_values],
            marker="o",
            fillstyle="none",
            color=colorslist[numberofdf],
            label=(args.desciption2[numberofdf][0].replace("\\n", "\n")),
            capsize=2,
        )

if args.relative:
    for numberofdf, df_avg in enumerate(df_avgs):
        speedup_values = df_avg[args.time].to_numpy()[0] / df_avg[args.time].to_numpy()
        print("speedup" + str(speedup_values))
        plt.plot(
            range(len(df_avg[args.time])),
            speedup_values,
            marker="o",
            fillstyle="none",
            label=(args.desciption2[numberofdf][0]).replace("\\n", "\n"),
        )

# Add labels and title
plt.xlabel(args.paramname if args.paramname else param)
plt.ylim(bottom=0)
if args.ylim > 0:
    plt.ylim(top=args.ylim)

if not args.speedup and not args.relative:
    plt.ylabel(args.yaxis)
    plt.title(
        args.title
        if args.title
        else f"Execution Time vs {args.paramname if args.paramname else param}"
    )
    # use minutes on y axis
    plt.gca().yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, _: f"{x/60:.0f}")
    )
else:
    plt.ylabel("Speedup")
    plt.title(
        args.title
        if args.title
        else (
            f"Speedup vs {args.paramname if args.paramname else param}"
            if args.speedup
            else f"Speedup Compared to Single Core Performance"
        )
    )
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:.1f}"))

    # # set yticks to percent
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
plt.xticks(
    median[param],
    [HumanBytes.format(int(h))[:-4] for h in median[param].to_numpy()],
    rotation=45,
    ha="right",
)

if args.desciption2:
    handles, labels = plt.gca().get_legend_handles_labels()
    if not args.speedup:
        order = [a[1] for a in sorted(max_values, key=lambda x: x[0], reverse=True)]
    else:
        order = [a[1] for a in sorted(max_values, key=lambda x: x[0], reverse=False)]
    plt.legend(
        [handles[idx] for idx in order],
        [labels[idx] for idx in order],
        ncol=args.ncols,
    )
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
