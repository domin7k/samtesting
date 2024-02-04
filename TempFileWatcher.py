from DelteAndCreateHandler import DelteAndCreateHandler


from watchdog.observers import Observer


import datetime


class TempFileWatcher:
    # Initialize the observer
    observer = None
    # Initialize the stop signal variable
    stop_signal = 0

    fileSizes = {}

    # The observer is the class that watches for any file system change and then dispatches the event to the event handler.
    def __init__(self, watchDirectory, totrack, result_dir, watchDelay, watchRecursively, doWatchDirectories):
        # Initialize variables in relation
        self.watchDirectory = watchDirectory
        self.totrack = totrack
        self.result_dir = result_dir
        self.watchDelay = watchDelay
        self.watchRecursively = watchRecursively
        self.doWatchDirectories = doWatchDirectories


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
            self.totrack(self.result_dir)
            self.stop()
        except Exception as error:
            print(error)
            self.stop()
        self.observer.join()

    def stop(self):
        self.event_handler.write_json()
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