# The Observer watches for any file change and then dispatches the respective events to an event handler.
# The event handler will be notified when an event occurs.
import datetime
import os
import shlex
import subprocess
from TempFileWatcher import TempFileWatcher
import config


def is_dir_path(path):
    """Utility function to check whether a path is an actual directory"""
    if os.path.isdir(path) or not os.path.exists(path):
        return path
    else:
        raise NotADirectoryError(path)


def runSam():
    with open("./samparams") as file:
        lines = [line.rstrip() for line in file]
    for line in lines:
        params = shlex.split(line)
        print(params)
        result = subprocess.run(["../samtools/samtools"] + params, capture_output=True, text=True)
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
    

if __name__ == "__main__":
    # define & launch the log watcher
    log_watcher = TempFileWatcher(
        watchDirectory=config.WATCH_DIRECTORY,
        totrack=runSam,
        watchDelay=config.WATCH_DELAY,
        watchRecursively=config.WATCH_RECURSIVELY,
        doWatchDirectories=config.DO_WATCH_DIRECTORIES,
    )
    log_watcher.run()