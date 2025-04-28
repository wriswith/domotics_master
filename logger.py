import logging
import time

from config.config import CONSOLE_LOG_LEVEL

class CustomFormatter(logging.Formatter):
    """Custom formatter to format time with milliseconds correctly."""
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = self.formatter_time = self.formatter_time = time.strftime(datefmt, ct)
        else:
            t = time.strftime("%Y-%m-%d %H:%M:%S", ct)
            s = f"{t}.{int(record.msecs):03d}"
        return s

def get_timestamp_logger():
    logger = logging.getLogger("console")
    logger.setLevel(CONSOLE_LOG_LEVEL)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create a formatter with a human-readable timestamp
    formatter = CustomFormatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Attach formatter to the handler
    console_handler.setFormatter(formatter)

    # Attach the handler to the logger
    logger.addHandler(console_handler)
    return logger


logger = get_timestamp_logger()
