import argparse


# add arguemnt to parser
parser = argparse.ArgumentParser(description="Calculate the time to consolidate files.")
parser.add_argument("run_number", type=int, help="The run number")
parser.add_argument("step", type=int, default=1, nargs="?")
args = parser.parse_args()


def get_times(j, max_tmp_files=64):
    time = 0
    n_big_files = 0
    n_files = 0

    big_files = []

    for i in range(0, j):
        consolidate_from = n_files
        is_big_merge = False

        if n_files - n_big_files >= max_tmp_files / 2:
            consolidate_from = n_big_files
            big_files.append(n_files - consolidate_from)
        elif n_files >= max_tmp_files:
            print(i)
            is_big_merge = True
            consolidate_from = 0
            time = time + sum(big_files)
            big_files = [sum(big_files)]

        time = time + 1 + (n_files - consolidate_from if (not is_big_merge) else 0)

        if consolidate_from < n_files:
            n_files = consolidate_from
            n_big_files = consolidate_from + 1

        n_files = n_files + 1
    return time


def get_times2(j, max_tmp_files=64):
    time = 0
    n_big_files = 0
    n_files = 0

    big_files = []

    for i in range(0, j):
        consolidate_from = n_files
        is_big_merge = False

        if (
            n_files - n_big_files >= max_tmp_files - n_big_files
            and n_big_files <= max_tmp_files
        ):
            consolidate_from = n_big_files
            big_files.append(n_files - consolidate_from)
        elif n_files >= max_tmp_files:
            is_big_merge = True
            consolidate_from = 0
            time = time + sum(big_files)
            big_files = [sum(big_files)]

        time = time + 1 + (n_files - consolidate_from if (not is_big_merge) else 0)

        if consolidate_from < n_files:
            n_files = consolidate_from
            n_big_files = consolidate_from + 1

        n_files = n_files + 1
    return time


# plot the results from get_times against get_times2 from 0 to args.run_number
import matplotlib.pyplot as plt

x = range(0, args.run_number + 1, args.step)
y1 = [get_times(i) for i in x]
print("generating times2")
y2 = [get_times2(i) for i in x]
y3 = [get_times(i, 1024) for i in x]
y4 = [get_times2(i, 1024) for i in x]

plt.plot(x, y1, label="default")
plt.plot(x, y2, label="allways max tmps")
plt.plot(x, y3, label="default but with up to 1024 tmp files")
plt.plot(x, y4, label="allways max tmps with up to 1024 tmp files")
plt.xlabel("Number of tmp files")
plt.ylabel("number of writes")
plt.title("Comparison of merge strategies")
plt.legend()
plt.show()
