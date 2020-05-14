""" Module for getting logger object

###############################################################################
# How to initialize logger when using the logger with pytest
###############################################################################

1) Import PiqeLogger class from piqe_utils.api.logger in main conftest.py
of the project.

2) Import __loggername__ from the project's __init__.py

3) Create a pytest fixture with (scope='session', autouse=True)
to initialize the logger in main conftest.py of the project.


i.e Add the following code in the project's conftest.py

import pytest
from piqe_utils.api.logger import PiqeLogger
from piqe_utils import __loggername__
# NOTE: You can also import __loggername__ from the project __init__.py

@pytest.fixture(scope='session', autouse=True)
def setup_logger():
    _ = PiqeLogger(__loggername__)

"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.getcwd(), "logs")
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
FILENAME = "piqe_logger_{}.log".format(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
FILEPATH = os.path.join(LOG_DIR, FILENAME)


class PiqeLogger(object):
    """ PIQE Logger class """
    _logger = None

    def __new__(cls, *args, **kwargs):
        if cls._logger is None:
            cls._logger = super(PiqeLogger, cls).__new__(cls)
            # Put any initialization here.
            cls._logger = logging.getLogger(args[0])
            cls._logger.setLevel(logging.DEBUG)

            # Create a file handler for logging level above DEBUG
            file_handler = RotatingFileHandler(FILEPATH,
                                               maxBytes=1024 * 1024 * 1024,
                                               backupCount=20)

            # Create a logging format
            log_formatter = logging.Formatter(
                '%(asctime)s - '
                '[%(levelname)s] - '
                '%(name)s - '
                '%(module)s@%(funcName)s:%(lineno)d - '
                '%(message)s')
            file_handler.setFormatter(log_formatter)

            # Create a stream handler for logging level above INFO
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            stream_handler.setFormatter(log_formatter)

            # Add the handlers to the logger
            cls._logger.addHandler(file_handler)
            cls._logger.addHandler(stream_handler)

        return cls._logger
