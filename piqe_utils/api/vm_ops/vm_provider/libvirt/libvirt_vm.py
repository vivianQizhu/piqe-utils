"""Module to define a libvirt domain object"""
from piqe_utils.api.vm_ops.vm_resource.core import BaseVM   # pylint: disable=import-error


class LibvirtVM(BaseVM):
    """
    Define the object for a libvirt domain
    """
    def __init__(self, domain_name, conn):
        """
        :param domain_name: The name of the libvirt domain
        :param conn: The libvirt connection object
        """
        self.domain_name = domain_name
        self.conn = conn
        self.libvirt_domain = self.conn.lookupByName(self.domain_name)

    @property
    def XMLDesc(self):
        """
        Get the real time xml description of libvirt domain
        """
        return self.libvirt_domain.XMLDesc()
