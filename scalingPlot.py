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

    avg = df.groupby(["params", "branch"], as_index=False)[args.time].median()

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
            avg[param],
            avg[args.time],
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


sizes = ["2.3", "23", "54.4", "108", "215"]

# Set xticks
plt.xticks(
    [i for (e, i) in enumerate(avg[param])],
    [str(8 * i) + ",\n" + sizes[e] for (e, i) in enumerate(avg[param])],
)

# plt.gca().xaxis.get_major_ticks()[1].tick1line.set_color("red")

# # add second x axis
# plt.twiny()
# ram = [str(8 * i) for (e, i) in enumerate(avg[param]) if e != 1]
# plt.xticks(
#     [i for (e, i) in enumerate(avg[param]) if e != 1],
#     ram,
# )

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
