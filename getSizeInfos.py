import argparse
import csv

from helpers.formating import HumanBytes

parser = argparse.ArgumentParser(
    description="Count the number of entries in a CSV file."
)
parser.add_argument("input", type=str, help="The input folder")
parser.add_argument(
    "compareto", type=str, help="The input folder to compare to", nargs="?"
)
args = parser.parse_args()

experiments = [args.input]
if args.compareto:
    experiments.append(args.compareto)

experiment_results = {}
for experiment in experiments:
    totalsize = {}
    times = {}
    with open(experiment + "/filesizes.csv", "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["run_counter"] != "0" or not "tmp" in row["file"]:
                continue
            branch = row["branch"]
            run_counter = row["run_counter"]
            params = row["params"]
            key = (branch, run_counter, params)
            totalsize[key] = totalsize.get(key, {})
            if row["file"] not in totalsize[key]:
                totalsize[key][row["file"]] = 0
            totalsize[key][row["file"]] = int(row["bytes"])

    with open(experiment + "/fileinfo.csv", "r") as timesfile:

        timesreader = csv.DictReader(timesfile)
        for row in timesreader:
            if (
                row["run_counter"] != "0"
                or not "tmp" in row["file"]
                or (row["operation"] != "writestart" and row["operation"] != "deleted")
            ):
                continue
            branch = row["branch"]
            run_counter = row["run_counter"]
            params = row["params"]
            key = (branch, run_counter, params)
            times[key] = times.get(key, {})
            if row["file"] not in times[key]:
                times[key][row["file"]] = [0, 0]
            if row["operation"] == "writestart":
                times[key][row["file"]][0] = row["timestamp"]
            if row["operation"] == "deleted":
                times[key][row["file"]][1] = row["timestamp"]

    # calculate statistics
    experiment_results[experiment] = {}
    for name, dic in times.items():
        drive_usage = 0
        sliding_usage: list = []
        max_usage = 0
        for file, data in sorted(dic.items(), key=lambda x: x[1][0]):
            start_time = data[0]
            file_size = totalsize[name][file]
            deleted = data[1]
            drive_usage += file_size
            sliding_usage = [
                value
                for value in sliding_usage
                if value[0][1] == 0 or value[0][1] > start_time
            ]
            sliding_usage.append([data, file_size])
            current_usage = 0
            for i in sliding_usage:
                current_usage += i[1]
            if current_usage > max_usage:
                max_usage = current_usage
        experiment_results[experiment][name] = (drive_usage, max_usage)

# print results
print(experiment_results)
for name, (drive_usage, max_usage) in experiment_results.get(args.input).items():
    print("---------------------------------")
    print(f"Branch: {name[0]}, Run: {name[1]}, Params: {name[2]}")
    print(f"Maximal concurrent drive usage: {HumanBytes.format(max_usage)}")
    if args.compareto:
        comp_key = (
            list(experiment_results.get(args.compareto).items())[0][0][0],
            name[1],
            name[2],
        )
        print(
            f"Maximal concurrent drive usage by {args.compareto}: {HumanBytes.format(experiment_results.get(args.compareto).get(comp_key)[1])}"
        )
        print(
            f"Ratio: {max_usage / experiment_results.get(args.compareto).get(comp_key)[1]}"
        )
    print(f"Total bytes written: {HumanBytes.format(drive_usage)}")
    if args.compareto:
        print(
            f"Total bytes written by {args.compareto}: {HumanBytes.format(experiment_results.get(args.compareto).get(comp_key)[0])}"
        )
        print(
            f"Ratio: {drive_usage / experiment_results.get(args.compareto).get(comp_key)[0]}"
        )

    print("---------------------------------")
