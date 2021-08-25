"""Module to perform libvirtd related operations"""

import os


def get_path(cmd):
    common_bin_paths = ["/usr/local/sbin", "/usr/sbin", "/sbin"]
    try:
        path_paths = os.environ['PATH'].split(":")
    except IndexError:
        path_paths = []
    path_paths = list(set(common_bin_paths + path_paths))

    for dir_path in path_paths:
        cmd_path = os.path.join(dir_path, cmd)
        if os.path.isfile(cmd_path):
            return os.path.abspath(cmd_path)


class Libvirtd(object):

    """
    Class to manage libvirtd service on host or guest.
    """
    def __init__(self, service_name="libvirtd"):
        self.service_name = service_name if get_path(service_name) else None

    def _wait_for_start(self, timeout=60):
        """
        Wait n seconds for libvirt to start.
        """

    def start(self, reset_failed=True):

    def stop(self):

    def restart(self, reset_failed=True):

    def is_running(self):
