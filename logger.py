import logging

from config.config import CONSOLE_LOG_LEVEL


def get_timestamp_logger():
    logger = logging.getLogger("console")
    logger.setLevel(CONSOLE_LOG_LEVEL)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create a formatter with a human-readable timestamp
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Attach formatter to the handler
    console_handler.setFormatter(formatter)

    # Attach the handler to the logger
    logger.addHandler(console_handler)
    return logger


logger = get_timestamp_logger()
