import logging
from logging.handlers import RotatingFileHandler
from sys import stdout

from constants import LOG_FILE, LOGGER_DT_FORMAT, LOGGER_FORMAT


def get_configured_logger(logger_name: str) -> logging.Logger:
    """Генерирует логгер по заданному имени."""
    logger = logging.getLogger(logger_name)

    logger.setLevel(logging.DEBUG)

    c_handler = logging.StreamHandler(stdout)
    f_handler = RotatingFileHandler(LOG_FILE,
                                    maxBytes=10**6,
                                    backupCount=5,
                                    encoding='UTF-8')

    formatter = logging.Formatter(fmt=LOGGER_FORMAT, datefmt=LOGGER_DT_FORMAT)
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger
