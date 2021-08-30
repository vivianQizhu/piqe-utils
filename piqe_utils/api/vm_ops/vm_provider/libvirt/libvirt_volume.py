"""Module to perform disk related operations on the domain"""
from piqe_utils.api.vm_ops.vm_resource.core import BaseVolume  # pylint:
# disable=import-error


class LibvirtVolume(BaseVolume):

    def __init__(self, dom):
        self.dom = dom

    def get_disk(self):
        pass

    def attach_disk(self):
        pass

    def detach_disk(self):
        pass

    def replace_disk(self):
        pass
