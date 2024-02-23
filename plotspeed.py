import argparse
import os
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker


PARAM = "-l"


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
    nargs="?",
)
# optionales zweites argument für zweites input csv
parser.add_argument(
    "-f",
    dest="filename2",
    type=str,
    help="The filename to get the csv data from.",
    default=None,
    nargs="?",
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


args = parser.parse_args()

param = args.param


def extractParam(param_string):
    if type(param_string) is not str:
        return "No Param"
    return param_string.strip().split(param)[1].strip().split(" ")[0]


# Read the CSV file
for file in [args.filename, args.filename2]:
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

    avg[param] = avg[param].apply(pd.to_numeric, errors="coerce")
    df_max[param] = df_max[param].apply(pd.to_numeric, errors="coerce")
    df_min[param] = df_min[param].apply(pd.to_numeric, errors="coerce")

    avg = avg.sort_values(by=[param])
    df_max = df_max.sort_values(by=[param])
    df_min = df_min.sort_values(by=[param])

    # print the mem column
    print(avg[param])

    # Plot the execution time against the 'mem' column
    plt.fill_between(
        x=range(len(avg["execution_time"])),
        y1=df_min["execution_time"].to_numpy(),
        y2=df_max["execution_time"].to_numpy(),
        alpha=0.20,
    )
    plt.plot(
        range(len(avg["execution_time"])),
        avg["execution_time"].to_numpy(),
        marker="o",
        fillstyle="none",
        label=(
            (args.desciption1 if file == args.filename else args.desciption2)
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
    )
    plt.plot(
        range(len(avg["execution_time"])),
        df_min["execution_time"].to_numpy(),
        marker=6,
        fillstyle="none",
        lw=0,
    )


# Add labels and title
plt.xlabel(args.paramname if args.paramname else param)
plt.ylabel("Execution Time")
plt.title(f"Execution Time vs {args.paramname if args.paramname else param}")
plt.ylim(bottom=0)

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
