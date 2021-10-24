import os
import sys
import logging
from flask import Flask

# from datetime import datetime
import json_logging

# from json_logging import BaseJSONFormatter, JSONLogFormatter, util
# will use above stuff to customize the logging later
from app.config.app_config import conf


def get_logger(name: str):
    logger = logging.getLogger(name=name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger


def init_logger(app: Flask):
    json_logging.init_flask(enable_json=True)
    json_logging.init_request_instrument(app)
