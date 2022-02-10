import os
import time
from ..report import Report, InvalidReport


class ReportWatcher:
    def __init__(self, path: str):
        path = os.path.expanduser(path)
        if not os.path.isdir(path):
            raise FileNotFoundError
        self.path = path

    def __iter__(self):
        lasttime = 0
        sizes = {}
        while True:
            now = time.time()
            paths = os.listdir(self.path)
            paths = [os.path.join(self.path, path) for path in paths]
            for path in paths:
                if os.path.isdir(path):
                    continue
                if path.endswith(".crdownload"):
                    continue
                size = os.path.getsize(path)
                if path not in sizes or sizes[path] != size:
                    sizes[path] = size
                    try:
                        report = Report.from_file(path)
                        yield report
                    except InvalidReport:
                        pass
            sleeptime = time.time() - lasttime
            if sleeptime > 1:
                time.sleep(1)
            elif sleeptime > 0:
                time.sleep(sleeptime)
            lasttime = now
