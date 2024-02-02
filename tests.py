# The Observer watches for any file change and then dispatches the respective events to an event handler.
# The event handler will be notified when an event occurs.
import os
from TempFileWatcher import TempFileWatcher
import config


# Class that inherits from FileSystemEventHandler for handling the events sent by the Observer
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