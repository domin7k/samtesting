import argparse
import os
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
parser.add_argument("filename", type=str, help="The filename to get the csv data from.")
parser.add_argument(
    "-d1",
    dest="desciption1",
    type=str,
    help="The description of the first csv file.",
    default=None,
    nargs="?",
)
parser.add_argument(
    "-d2",
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

print(args.filename2)
print(args.desciption2)
# Read the CSV file
for no, file in enumerate(
    [args.filename] + [item for row in args.filename2 for item in row]
):
    if not file:
        continue

    df = pd.read_csv(file)

    avg = df.groupby(["params", "branch"], as_index=False)["execution_time"].mean()

    df_min = df.groupby(["params", "branch"], as_index=False)["execution_time"].min()
    df_max = df.groupby(["params", "branch"], as_index=False)["execution_time"].max()
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

        # Plot the execution time against the 'mem' column
        plt.fill_between(
            x=range(len(avg["execution_time"])),
            y1=df_min["execution_time"].to_numpy(),
            y2=df_max["execution_time"].to_numpy(),
            alpha=0.20,
            color=colorslist[no],
        )
        plt.plot(
            range(len(avg["execution_time"])),
            avg["execution_time"].to_numpy(),
            marker="o",
            fillstyle="none",
            color=colorslist[no],
            label=(
                (
                    args.desciption1
                    if file == args.filename
                    else args.desciption2[no - 1][0]
                )
                if args.desciption1 and args.desciption2
                else None
            ),
        )
        plt.plot(
            range(len(avg["execution_time"])),
            df_max["execution_time"].to_numpy(),
            marker=7,
            fillstyle="none",
            lw=0,
            color=colorslist[no],
        )
        plt.plot(
            range(len(avg["execution_time"])),
            df_min["execution_time"].to_numpy(),
            marker=6,
            fillstyle="none",
            lw=0,
            color=colorslist[no],
        )

    else:
        df_mins.append(df_min)
        df_maxs.append(df_max)
        df_avgs.append(avg)

speedup_values = []
if args.speedup:
    speedup_values = (
        df_avgs[1]["execution_time"].to_numpy()
        / df_avgs[0]["execution_time"].to_numpy()
    )
    plt.plot(
        range(len(df_avgs[0]["execution_time"])),
        speedup_values,
        marker="o",
        fillstyle="none",
        label=(
            (args.desciption2 + "/" + args.desciption1)
            if args.desciption1 and args.desciption2
            else None
        ),
    )


# Add labels and title
plt.xlabel(args.paramname if args.paramname else param)
plt.ylim(bottom=0)

if not args.speedup:
    plt.ylabel("Execution Time")
    plt.title(f"Execution Time vs {args.paramname if args.paramname else param}")
else:
    plt.ylabel("Speedup")
    plt.title(f"Speedup vs {args.paramname if args.paramname else param}")
    # set yticks to percent
    plt.gca().yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))
    for i, v in enumerate(speedup_values):
        plt.annotate(
            f"{v:.2%}",
            xy=(i, v),
            xytext=(0, -7),
            textcoords="offset points",
            ha="center",
            va="top",
        )


# Set xticks
plt.xticks(range(len(avg["execution_time"])), avg[param])

if args.desciption1 and args.desciption2:
    plt.legend()

fig1 = plt.gcf()
# Show the plot
plt.show()
if input("Do you want to save the plot? (y/n) ").lower() == "y":
    if args.filename2:

        fig1.savefig(
            f"{os.path.dirname(args.filename)+'/'+os.path.basename(args.filename)}_vs_{args.filename2.split('/')[-2]}_plot.png"
        )
    else:
        fig1.savefig(
            f"{os.path.dirname(args.filename) +'/'+ os.path.basename(args.filename).split('.')[0]}_plot.png"
        )
