# The Observer watches for any file change and then dispatches the respective events to an event handler.
# The event handler will be notified when an event occurs.
import argparse
import datetime
import json
import os
import resource
import shlex
import shutil
import subprocess
import time
import traceback

import pandas as pd
import psutil
from TempFileWatcher import TempFileWatcher
import config
from helpers.formating import HumanBytes
from prepare_dirs import delete_old_dirs

# from plotfiles import human_format


def is_dir_path(path):
    """Utility function to check whether a path is an actual directory"""
    if os.path.isdir(path) or not os.path.exists(path):
        return path
    else:
        raise NotADirectoryError(path)


def getVersions():
    return {
        "samtoolsVersion": subprocess.check_output(
            ["git", "--git-dir", "../samtools/.git", "rev-parse", "HEAD"]
        )
        .decode("ascii")
        .strip(),
        "htslibVersion": subprocess.check_output(
            ["git", "--git-dir", "../htslib/.git", "rev-parse", "HEAD"]
        )
        .decode("ascii")
        .strip(),
        "samtoolsBranch": subprocess.check_output(
            [
                "git",
                "--git-dir",
                "../samtools/.git",
                "rev-parse",
                "--abbrev-ref",
                "HEAD",
            ]
        )
        .decode("ascii")
        .strip(),
        "htslibBranch": subprocess.check_output(
            ["git", "--git-dir", "../htslib/.git", "rev-parse", "--abbrev-ref", "HEAD"]
        )
        .decode("ascii")
        .strip(),
    }


def runSam(result_dir: str, run_counter=0, preargs=""):
    print("---------------------------------")
    print(f"Runing repetion: {run_counter + 1}/{args.reps}")
    print("---------------------------------")

    if not os.path.exists(f"{result_dir}/results.csv"):
        with open(f"{result_dir}/results.csv", "w") as csvFile:
            csvFile.write(
                "run_counter,branch,params,user_time,system_time,execution_time,io_wait\n"
            )

    with open(config.TEMP_SAMPARAMS, "r") as file:
        lines = [line.rstrip() for line in file]

    versionCounter = 0
    versions = getVersions()

    for line in lines:
        if line.strip().startswith("("):
            if "checkout" in line:
                if versions["samtoolsBranch"] in line:
                    print("Samtools branch already checked out")
                    continue

            subprocess.run(line, shell=True)
            # run make clean and make in the git directory
            git_dir = os.path.dirname(line.split("cd")[1].strip().split(" ")[0].strip())
            # subprocess.run([f"(cd {git_dir}/ && make clean)"], shell=True)
            subprocess.run([f"(cd {git_dir}/ && make)"], shell=True)
            versions = getVersions()
            versionCounter += 1
            json.dump(
                versions,
                open(f"{result_dir}/versions{versionCounter}.json", "w"),
            )
            continue

        params = shlex.split(line)
        print(f"Params: {params}")
        start_time = time.time()
        start_resources = resource.getrusage(resource.RUSAGE_CHILDREN)
        start_io_wait = psutil.cpu_times().iowait

        if not "sambamba" in line:
            result = subprocess.run(
                preargs + "samtools " + " ".join(params),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
        else:
            result = subprocess.run(
                " ".join(params),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )

        end_io_wait = psutil.cpu_times().iowait

        end_resources = resource.getrusage(resource.RUSAGE_CHILDREN)
        end_time = time.time()

        execution_time = end_time - start_time
        user_time = end_resources.ru_utime - start_resources.ru_utime
        system_time = end_resources.ru_stime - start_resources.ru_stime
        io_wait_time = end_io_wait - start_io_wait

        print(f"Execution time: {execution_time} seconds")
        print(f"User time: {user_time} seconds")
        with open(f"{result_dir}/results.csv", "a") as csvFile:
            csvFile.write(
                f"{run_counter},{versions['samtoolsBranch']},{line},{user_time},{system_time},{execution_time},{io_wait_time}\n"
            )

        stderr = result.stderr.decode("ascii")
        if not os.path.exists(f"{result_dir}/fileinfo.csv"):
            with open(f"{result_dir}/fileinfo.csv", "w") as file:
                file.write("run_counter,branch,params,operation,file,timestamp\n")
        if not os.path.exists(f"{result_dir}/filesizes.csv"):
            with open(f"{result_dir}/filesizes.csv", "w") as file:
                file.write("run_counter,branch,params,file,bytes\n")

        with open(f"{result_dir}/fileinfo.csv", "a") as file:
            for info in stderr.split("\n"):
                if not info.strip().startswith("[time-info]"):
                    continue
                parts = info.strip().split()
                file.write(
                    f"{run_counter},{versions['samtoolsBranch']},{line},{parts[1]},{parts[2]},{parts[3]}\n"
                )
        with open(f"{result_dir}/filesizes.csv", "a") as file:
            for info in stderr.split("\n"):
                if not info.strip().startswith("[size-info]"):
                    continue
                parts = info.strip().split()
                file.write(
                    f"{run_counter},{versions['samtoolsBranch']},{line},{parts[1]},{parts[2]}\n"
                )
        print(stderr)
        print(result.stdout.decode("ascii"))


if __name__ == "__main__":

    # # define & launch the log watcher
    # log_watcher = TempFileWatcher(
    #     watchDirectory=config.WATCH_DIRECTORY,
    #     totrack=runSam,
    #     result_dir=result_dir,
    #     watchDelay=config.WATCH_DELAY,
    #     watchRecursively=config.WATCH_RECURSIVELY,
    #     doWatchDirectories=config.DO_WATCH_DIRECTORIES,
    # )
    # log_watcher.run()

    parser = argparse.ArgumentParser(
        description="Run samtools with different parameters"
    )
    parser.add_argument("reps", type=int, help="The number of repetitions")
    parser.add_argument("-ld", dest="preargs", type=str, help="The preargs", default="")
    parser.add_argument(
        "-d", dest="result_dir", type=str, help="The result directory", default=""
    )
    args = parser.parse_args()
    result_dir = (
        config.TEST_RESULT_DIR
        + f"/{datetime.datetime.now().isoformat() + args.result_dir}"
    )
    os.makedirs(result_dir)
    try:
        # open a cvs file in the result directory and write the header
        # make a copy of the samparams file
        shutil.copyfile(config.TEMP_SAMPARAMS, f"{result_dir}/samparams")
        # ask the user for information about the experiment and store the input in a file named comment.txt
        # if the imput is empty, the file will not be created
        # comment = input("Please enter a comment for the experiment: ")
        # if comment:
        #     with open(f"{result_dir}/comment.txt", "w") as file:
        #         file.write(comment)

        versions = getVersions()
        json.dump(versions, open(f"{result_dir}/versionsStart.json", "w"))
        with open(f"{result_dir}/preargs.txt", "w") as file:
            file.write(args.preargs)
        for i in range(args.reps):
            delete_old_dirs(ask=False)
            runSam(result_dir, i, args.preargs)

        print("All runs finished")
        print("results written to: " + os.path.abspath(result_dir))

    except Exception as e:
        print(traceback.format_exc())
        # ask the user if he wants to delete the result directory
        delete = input("Do you want to delete the result directory? (y/n)")
        if delete == "y":
            shutil.rmtree(result_dir)
        else:
            print("The result directory was not deleted")
        exit(1)


# # collect filesizes in a json file
# branches = []
# # get the branches from the branch column of the csv file using pandas
# df = pd.read_csv(result_dir + "/results.csv")
# branches = df["branch"].tolist()
# print(f"branches: {branches}")
# temFiles = {}
# with open(config.TEMP_SAMPARAMS, "r") as file:
#     for line in file:
#         if line.strip() z== "" or line.strip().startswith("("):
#             continue

#         line = line.strip()
#         if "-o" in line:
#             branch = branches.pop(0)
#             output_dir = os.path.dirname(line.split("-o")[1].strip().split(" ")[0])
#             if os.path.exists(output_dir + "/fileSizes.json"):
#                 with open(output_dir + "/fileSizes.json", "r") as file:
#                     singleRunTemps = json.load(file)
#                     # add to summary
#                     for key in singleRunTemps:
#                         onlyFileName = os.path.basename(key)
#                         if onlyFileName in temFiles:
#                             temFiles[onlyFileName][branch + ": " + line] = (
#                                 singleRunTemps[key]
#                             )
#                         else:
#                             temFiles[onlyFileName] = {
#                                 branch + ": " + line: singleRunTemps[key]
#                             }

#                     # calculate statistics
#                     drive_usage = 0
#                     sliding_usage: list = []
#                     max_usage = 0
#                     for name, data in sorted(
#                         singleRunTemps.items(), key=lambda x: x[0]
#                     ):
#                         print(data)
#                         start_time = data["creation_time"]
#                         end_time = data["last_modified"]
#                         file_size = data["size"]
#                         deleted = data["deleted"]
#                         drive_usage += file_size
#                         sliding_usage = [
#                             value
#                             for value in sliding_usage
#                             if value["deleted"] == 0
#                             or value["deleted"] > start_time
#                         ]
#                         sliding_usage.append(data)
#                         current_usage = 0
#                         for i in sliding_usage:
#                             current_usage += i["size"]
#                         if current_usage > max_usage:
#                             max_usage = current_usage
#                 print(f"command: {line}")
#                 print(
#                     f"Maximal concurrent drive usage: {HumanBytes.format(max_usage)}"
#                 )
#                 print(f"Total bytes written: {HumanBytes.format(drive_usage)}")
#                 print("---------------------------------")

# with open(result_dir + "/fileSizes.json", "w") as file:
#     json.dump(temFiles, file, indent=4)
