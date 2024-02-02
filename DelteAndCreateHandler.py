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