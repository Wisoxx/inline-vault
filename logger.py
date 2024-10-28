import logging
from logging.handlers import RotatingFileHandler
import os
import io
import sys


def setup_logger(name):
    log_path = os.path.join(os.path.expanduser("~"), 'mysite', 'logs')
    os.makedirs(log_path, exist_ok=True)

    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        file_handler = RotatingFileHandler(os.path.join(log_path, 'app.log'), maxBytes=1000000, backupCount=4)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'))
        console_formatter = logging.Formatter('%(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.DEBUG)
        console_handler.encoding = 'utf-8'

        logger.setLevel(logging.DEBUG)  # lowest level to allow separate levels for files and console
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
