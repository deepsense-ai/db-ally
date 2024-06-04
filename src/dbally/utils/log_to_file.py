import sys


class FileLogger:
    """
    A class for logging messages to both a file and the console.

    Args:
        filename: The name of the file to log messages to.

    Attributes:
        log_file: The file object for logging messages.
        console: The standard output stream for logging messages.
    """

    def __init__(self, filename):
        """
        Initializes the FileLogger with the specified filename.

        Args:
            filename: The name of the file to log messages to.
        """
        self.log_file = None
        with open(filename, "w", encoding="utf8") as log_file:
            self.log_file = log_file

        self.console = sys.stdout

    def write(self, message: str):
        """
        Writes the given message to both the log file and the console.

        Args:
            message: The message to be logged.
        """
        self.log_file.write(message)
        self.console.write(message)

    def flush(self):
        """
        Flushes both the log file and the console, ensuring all buffered output is written.
        """
        self.log_file.flush()
        self.console.flush()

    def isatty(self):
        """
        Returns False, indicating that this class does not represent a tty.

        Returns:
            bool: Always returns False.
        """
        return False
