# The Observer watches for any file change and then dispatches the respective events to an event handler.
import shutil
import subprocess
from watchdog.observers import Observer
# The event handler will be notified when an event occurs.
from watchdog.events import FileSystemEventHandler
import time
import os
import datetime
import config
from colorama import Fore, Style, init

init()

GREEN = Fore.GREEN
BLUE = Fore.BLUE
RED = Fore.RED
YELLOW = Fore.YELLOW

event2color = {
    "created": GREEN,
    "modified": BLUE,
    "deleted": RED,
    "moved": YELLOW,
}


def print_with_color(s, color=Fore.WHITE, brightness=Style.NORMAL, size=-1, **kwargs):
    """Utility function wrapping the regular `print()` function 
    but with colors and brightness"""
    print(f"{brightness}{color}{s}{Style.RESET_ALL}{size if size>0 else''}", **kwargs)

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

# Class that inherits from FileSystemEventHandler for handling the events sent by the Observer
class DelteAndCreateHandler(FileSystemEventHandler):
    lastFile= None
    fileSizes: dict = {}

    def __init__(self, doWatchDirectories, fileSizes):
        self.doWatchDirectories = doWatchDirectories
        self.fileSizes=fileSizes

    def on_any_event(self, event):
        pass

    def on_modified(self, event):
        pass

    def on_deleted(self, event):
        now = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        self.fileSizes[event.src_path][3] = datetime.datetime.now()
        path = event.src_path
        msg = f"{now} -- {event.event_type} -- File: {path}"
        print_with_color(msg, color=event2color[event.event_type])

    def on_created(self, event):
        now = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        if(self.lastFile!=None):
            self.fileSizes[self.lastFile][1]=datetime.datetime.now()
            self.fileSizes[self.lastFile][2]=os.path.getsize(self.lastFile)
            print(self.fileSizes[self.lastFile])
        self.lastFile = event.src_path
        self.fileSizes[self.lastFile] = [datetime.datetime.now(),0,0,0]
        path = event.src_path
        msg = f"{now} -- {event.event_type} -- File: {path}"
        print_with_color(msg, color=event2color[event.event_type])

    def on_moved(self, event):
        pass


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
            directory = self.watchDirectory
            out = f"{directory}/sorted.bam"
            samtools = subprocess.run(["../samtools/samtools", "sort", self.fileName, "-o", out, "-m", "200M"])
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
            print
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


def is_dir_path(path):
    """Utility function to check whether a path is an actual directory"""
    if os.path.isdir(path) or not os.path.exists(path):
        return path
    else:
        raise NotADirectoryError(path)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Watchdog script for watching for files & directories' changes")
    parser.add_argument("path",
                        default=config.WATCH_DIRECTORY,
                        type=is_dir_path,
                        )
    parser.add_argument("-n", "--name",
                        help=f"name of the file to be sorted",
                        default="test.bam",
                        type=str,
                        )
    parser.add_argument("-d", "--watch-delay",
                        help=f"Watch delay, default is {config.WATCH_DELAY}",
                        default=config.WATCH_DELAY,
                        type=int,
                        )
    parser.add_argument("-r", "--recursive",
                        action="store_true",
                        help=f"Whether to recursively watch for the path's children, default is {config.WATCH_RECURSIVELY}",
                        default=config.WATCH_RECURSIVELY,
                        )
    parser.add_argument("--watch-directories",
                        action="store_true",
                        help=f"Whether to watch directories, default is {config.DO_WATCH_DIRECTORIES}",
                        default=config.DO_WATCH_DIRECTORIES,
                        )
    # parse the arguments
    args = parser.parse_args()
    # define & launch the log watcher
    log_watcher = TempFileWatcher(
        watchDirectory=args.path,
        fileName = args.name,
        watchDelay=args.watch_delay,
        watchRecursively=args.recursive,
        doWatchDirectories=args.watch_directories,
    )
    log_watcher.run()