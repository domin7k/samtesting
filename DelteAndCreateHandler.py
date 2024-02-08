import json
from colorama import Fore, Style, init
from watchdog.events import FileSystemEventHandler


import datetime
import os

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

class DelteAndCreateHandler(FileSystemEventHandler):
    lastFile= None
    fileSizes: dict = {}
    is_stopped = False

    def __init__(self, doWatchDirectories, fileSizes):
        self.doWatchDirectories = doWatchDirectories
        self.fileSizes=fileSizes

    def on_any_event(self, event):
        pass

    def on_modified(self, event):
        if event.src_path == self.lastFile:
            print_with_color(f"File {event.src_path} was modified after creation of another file", color=Fore.CYAN)
            print(self.fileSizes[self.lastFile])

    def on_deleted(self, event):
        now = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        path = event.src_path
        self.fileSizes[path][3] = datetime.datetime.now().timestamp()
        msg = f"{now} -- {event.event_type} -- File: {path}"
        print_with_color(msg, color=event2color[event.event_type])

    def on_created(self, event):
        if self.is_stopped:
            return
        now = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        if(self.lastFile!=None):
            self.fileSizes[self.lastFile][1]=os.path.getmtime(self.lastFile) if os.path.exists(self.lastFile) else -1
            self.fileSizes[self.lastFile][2]=os.path.getsize(self.lastFile) if os.path.exists(self.lastFile) else -1
            print(self.fileSizes[self.lastFile])
        path = event.src_path
        self.lastFile = path
        self.fileSizes[path] = [os.stat(path).st_ctime,0,0,0]
        
        msg = f"{now} -- {event.event_type} -- File: {path}"
        print_with_color(msg, color=event2color[event.event_type])

    

    def on_moved(self, event):
        pass
    
    def write_json(self):
        self.is_stopped = True
        if(self.lastFile!=None and self.fileSizes[self.lastFile][1]== 0):
                self.fileSizes[self.lastFile][1]=os.path.getmtime(self.lastFile)
                self.fileSizes[self.lastFile][2]=os.path.getsize(self.lastFile)
                print(self.fileSizes[self.lastFile])
        dirOfDirs = {}
        for key in self.fileSizes:
            # get the directory of the file
            directory = os.path.dirname(key)
            if directory not in dirOfDirs:
                dirOfDirs[directory] = {}
            dirOfDirs[directory][key] = {"creation_time": self.fileSizes[key][0], "last_modified": self.fileSizes[key][1], "size": self.fileSizes[key][2], "deleted": self.fileSizes[key][3]}
        # write the dictionary to a json file in the directory that is key of the dirOfDirs
        for key in dirOfDirs:
            with open(f"{key}/fileSizes.json", "w") as file:
                json.dump(dirOfDirs[key], file, indent=4)

        