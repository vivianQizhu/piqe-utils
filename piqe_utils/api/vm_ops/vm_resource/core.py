"""Abstract the base class for VM And Volumn"""

class BaseVM(object):

    """
    The base class for VM definition, implement the vm related operations like
    to reboot and gracefully shutdown.
    """

    def reboot(self):
        """
        Reboot the VM, which should be implement on specific type VM class
        """
        raise NotImplementedError

    def graceful_shutdown(self):
        """
        Gracefully shutdown the VM, which should be implement on specific type
         VM class"""
        raise NotImplementedError


class BaseVolume(object):

    """
    The base class for VM Volume definition, implement the operation of
    certain volume related operations, e.g. attach disk, detach disk, replace
    the disk image.
    """

    def get_disk(self):
        """
        Get disk information, which should be implement on specific
         type VM volume class
        """
        raise NotImplementedError

    def attach_disk(self):
        """
        Attach disk to VM, which should be implement on specific
         type VM volume class
        """
        raise NotImplementedError

    def detach_disk(self):
        """
        Detach disk from VM, which should be implement on specific
         type VM volume class
        """
        raise NotImplementedError

    def replace_disk(self):
        """
        Replace disk image of VM, which should be implement on specific
         type VM volume class
        """
        raise NotImplementedError
