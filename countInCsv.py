import argparse
import csv

parser = argparse.ArgumentParser(
    description="Count the number of entries in a CSV file."
)
parser.add_argument("input", type=str, help="The input file")
args = parser.parse_args()


def count_entries(csv_file):
    counts = {}

    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            branch = row["branch"]
            run_counter = row["run_counter"]
            params = row["params"]

            key = (branch, run_counter, params)
            counts[key] = counts.get(key, 0) + 1

    return counts


entry_counts = count_entries(args.input)

for key, count in entry_counts.items():
    branch, run_counter, params = key
    print(
        f"Combination: branch={branch}, run_counter={run_counter}, params={params} - Count: {count}"
    )
