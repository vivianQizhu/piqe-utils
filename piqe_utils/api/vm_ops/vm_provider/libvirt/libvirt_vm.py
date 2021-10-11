"""Module to define a libvirt domain object"""
import libvirt
from piqe_utils import __loggername__
from piqe_utils.api.logger import PiqeLogger
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
        self.logger = PiqeLogger(__loggername__)

    @property
    def XMLDesc(self):
        """
        Get the real time xml description of libvirt domain
        """
        return self.libvirt_domain.XMLDesc()

    def reboot(self):
        """
        Reboot the VM
        """
        try:
            ret = self.libvirt_domain.reboot()
        except libvirt.libvirtError as err:
            self.logger.error(f"API error message: {err.get_error_message()}")
        return ret
    def graceful_shutdown(self):
        """
        Gracefully shutdown the VM
        """
        try:
            ret = self.libvirt_domain.destroyFlags(libvirt.VIR_DOMAIN_DESTROY_GRACEFUL)
        except libvirt.libvirtError as err:
            self.logger.error(f"API error message: {err.get_error_message()}")
        return ret