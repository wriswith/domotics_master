import logging
import time

from config.config import CONSOLE_LOG_LEVEL


def get_timestamp_logger():
    new_logger = logging.getLogger("console")
    new_logger.setLevel(CONSOLE_LOG_LEVEL)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create a formatter with a human-readable timestamp
    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Attach formatter to the handler
    console_handler.setFormatter(formatter)

    # Attach the handler to the logger
    new_logger.addHandler(console_handler)
    return new_logger


logger = get_timestamp_logger()
