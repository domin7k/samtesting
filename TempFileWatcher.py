import shutil
from DelteAndCreateHandler import DelteAndCreateHandler


from watchdog.observers import Observer


import datetime
import os
import shlex
import subprocess

def create_or_clear_directory(directory_path, prefix="sorted"):
    if os.path.exists(directory_path):
        files = os.listdir(directory_path)
        if all(file.startswith(prefix) for file in files):
            shutil.rmtree(directory_path)
            print(f"Deleted {directory_path}.")
        else:
            print(f"{directory_path} contains files not starting with '{prefix}'.")
            exit(-1)
    os.makedirs(directory_path)


class TempFileWatcher:
    # Initialize the observer
    observer = None
    # Initialize the stop signal variable
    stop_signal = 0

    fileSizes = {}

    # The observer is the class that watches for any file system change and then dispatches the event to the event handler.
    def __init__(self, watchDirectory, fileName, watchDelay, watchRecursively, doWatchDirectories):
        # Initialize variables in relation
        self.watchDirectory = watchDirectory
        self.fileName = fileName
        self.watchDelay = watchDelay
        self.watchRecursively = watchRecursively
        self.doWatchDirectories = doWatchDirectories
        create_or_clear_directory(watchDirectory)


        # Create an instance of watchdog.observer
        self.observer = Observer()

        # The event handler is an object that will be notified when something happens to the file system.
        self.event_handler = DelteAndCreateHandler(self.doWatchDirectories, self.fileSizes)

    def schedule(self):
        print("Observer Scheduled:", self.observer.name)
        # Call the schedule function via the Observer instance attaching the event
        self.observer.schedule(
            self.event_handler, self.watchDirectory, recursive=self.watchRecursively)

    def start(self):
        print("Observer Started:", self.observer.name)
        self.schedule()
        # Start the observer thread and wait for it to generate events
        now = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        msg = f"Observer: {self.observer.name} - Started On: {now}"
        print(msg)

        msg = (
            f"Watching {'Recursively' if self.watchRecursively else 'Non-Recursively'}"
            f" -- Folder: {self.watchDirectory} -- Every: {self.watchDelay}(sec)"
        )
        print(msg)
        self.observer.start()

    def run(self):
        print("Observer is running:", self.observer.name)
        self.start()
        try:
            with open("./samparams") as file:
                lines = [line.rstrip() for line in file]
            for line in lines:
                params = shlex.split(line)
                print(params)
                directory = self.watchDirectory
                out = f"{directory}/sorted.bam"
                result = subprocess.run(["../samtools/samtools"] + params, capture_output=True)
                print(result.stdout)
                self.fileSizes[out][1]=datetime.datetime.now()
                self.fileSizes[out][2]=os.path.getsize(out)
                drive_usage = 0
                sliding_usage: list = []
                max_usage = 0
                for name, data in sorted(self.fileSizes.items(), key=lambda x : x[0]):
                    start_time = data[0]
                    end_time = data[1]
                    duration = end_time - start_time
                    file_size = data[2]
                    deleted = data[3]
                    drive_usage += file_size
                    sliding_usage = [value for value in sliding_usage if value[3] == 0 or value[3] > start_time]
                    sliding_usage.append(data)
                    current_usage = 0
                    for i in sliding_usage:
                        current_usage += i[2]
                    if (current_usage>max_usage):
                        max_usage = current_usage
                    print(f"Name: {name}")
                    print(f"Active Time: {duration}")
                    print(f"final size: {file_size} Bytes")
                    print(f"deleted at {deleted}")
                    print("------------------------")
            print(f"Maximal concurrent drive usage: {max_usage}")
            print(f"Total bytes written: {drive_usage}")
            self.stop()
        except Exception as error:
            print(error)
            self.stop()
        self.observer.join()

    def stop(self):
        print("Observer Stopped:", self.observer.name)

        now = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        msg = f"Observer: {self.observer.name} - Stopped On: {now}"
        print(msg)
        self.observer.stop()
        self.observer.join()

    def info(self):
        info = {
            'observerName': self.observer.name,
            'watchDirectory': self.watchDirectory,
            'watchDelay': self.watchDelay,
            'watchRecursively': self.watchRecursively,
            'watchPattern': self.watchPattern,
        }
        return info