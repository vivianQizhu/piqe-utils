"""Module to define a libvirt domain object"""
from piqe_utils.api.vm_ops.vm_resource.core import BaseVM   # pylint: disable=import-error


class LibvirtVM(BaseVM):
    """
    Define the object Domain
    """
    def __init__(self, domain_name, conn):
        self.domain_name = domain_name
        self.conn = conn
        self.dom = self.conn.lookupByName(domain_name)
        self.info = self.dom.info()
        self.domxml = self.dom.XMLDesc(0)

    def reboot(self):
        pass

    def graceful_shutdown(self):
        pass
