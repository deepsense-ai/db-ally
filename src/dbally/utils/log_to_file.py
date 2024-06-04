import sys


class FileLogger:
    def __init__(self, filename):
        self.logFile = open(filename, "w")
        self.console = sys.stdout

    def write(self, message):
        self.logFile.write(message)
        self.console.write(message)

    def flush(self):
        self.logFile.flush()
        self.console.flush()

    def isatty(self):
        return False
