import pytest

from piqe_utils.api.logger import PiqeLogger
from piqe_utils import __loggername__


@pytest.fixture(scope="session", autouse=True)
def setup_logger():
    logger = PiqeLogger(__loggername__)
    return logger


def pytest_configure(config):
    marker_list = ['libvirt']
    for maker in marker_list:
        config.addinivalue_line('markers', maker)
