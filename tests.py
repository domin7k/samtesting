# The Observer watches for any file change and then dispatches the respective events to an event handler.
# The event handler will be notified when an event occurs.
import datetime
import json
import os
import resource
import shlex
import shutil
import subprocess
import time
from TempFileWatcher import TempFileWatcher
import config


def is_dir_path(path):
    """Utility function to check whether a path is an actual directory"""
    if os.path.isdir(path) or not os.path.exists(path):
        return path
    else:
        raise NotADirectoryError(path)


def runSam(result_dir: str):
    try:
        # open a cvs file in the result directory and write the header
        # make a copy of the samparams file
        shutil.copyfile("samparams", f"{result_dir}/samparams")
        # ask the user for information about the experiment and store the input in a file named comment.txt
        # if the imput is empty, the file will not be created
        comment = input("Please enter a comment for the experiment: ")
        if comment:
            with open(f"{result_dir}/comment.txt", "w") as file:
                file.write(comment)

        versions = {"samtoolsVersion" : subprocess.check_output(["git", "--git-dir", "../samtools/.git", "rev-parse", "HEAD"]).decode("ascii").strip(),
                    "htslibVersion" : subprocess.check_output(["git", "--git-dir", "../htslib/.git", "rev-parse", "HEAD"]).decode("ascii").strip(),
                    }
        json.dump(versions, open(f"{result_dir}/versions.json", "w"))

        with open(f"{result_dir}/results.csv", "w") as csvFile:
            csvFile.write("params,user_time,system_time,memory_usage,execution_time\n")
            with open("./samparams") as file:
                lines = [line.rstrip() for line in file]
            for line in lines:
                params = shlex.split(line)
                print(f"Params: {params}")
                start_time = time.time()
                start_resources = resource.getrusage(resource.RUSAGE_CHILDREN)

                result = subprocess.run(["../samtools/samtools"] + params, capture_output=True, text=True)

                end_resources = resource.getrusage(resource.RUSAGE_CHILDREN)
                end_time = time.time()

                execution_time = end_time - start_time
                user_time = end_resources.ru_utime - start_resources.ru_utime
                system_time = end_resources.ru_stime - start_resources.ru_stime
                # the same for all resources
                memory_usage = end_resources.ru_maxrss

                print(f"Execution time: {execution_time} seconds")
                print(f"User time: {user_time} seconds")
                print(f"Memory usage: {memory_usage} kilobytes")
                csvFile.write(f"{line},{user_time},{system_time},{memory_usage},{execution_time}\n")
                print(result.stderr)
                print(result.stdout)
            #     drive_usage = 0
            #     sliding_usage: list = []
            #     max_usage = 0
            #     for name, data in sorted(self.fileSizes.items(), key=lambda x : x[0]):
            #         start_time = data[0]
            #         end_time = data[1]
            #         duration = end_time - start_time
            #         file_size = data[2]
            #         deleted = data[3]
            #         drive_usage += file_size
            #         sliding_usage = [value for value in sliding_usage if value[3] == 0 or value[3] > start_time]
            #         sliding_usage.append(data)
            #         current_usage = 0
            #         for i in sliding_usage:
            #             current_usage += i[2]
            #         if (current_usage>max_usage):
            #             max_usage = current_usage
            #         print(f"Name: {name}")
            #         print(f"Active Time: {duration}")
            #         print(f"final size: {file_size} Bytes")
            #         print(f"deleted at {deleted}")
            #         print("------------------------")
            # print(f"Maximal concurrent drive usage: {max_usage}")
            # print(f"Total bytes written: {drive_usage}")
    except Exception as e:
        print(e)
        print("An error occurred")
        # ask the user if he wants to delete the result directory
        delete = input("Do you want to delete the result directory? (y/n)")
        if delete == "y":
            shutil.rmtree(result_dir)
        else:
            print("The result directory was not deleted")

    



if __name__ == "__main__":
    result_dir = config.TEST_RESULT_DIR + f"/{datetime.datetime.now().isoformat()}"
    os.makedirs(result_dir)
    # define & launch the log watcher
    log_watcher = TempFileWatcher(
        watchDirectory=config.WATCH_DIRECTORY,
        totrack=runSam,
        result_dir=result_dir,
        watchDelay=config.WATCH_DELAY,
        watchRecursively=config.WATCH_RECURSIVELY,
        doWatchDirectories=config.DO_WATCH_DIRECTORIES,
    )
    log_watcher.run()