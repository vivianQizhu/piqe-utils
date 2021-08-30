"""Abstract the base class for VM And Volumn"""

class BaseVM(object):

    def reboot(self):
        raise NotImplementedError

    def graceful_shutdown(self):
        raise NotImplementedError


class BaseVolume(object):

    def get_disk(self):
        raise NotImplementedError

    def attach_disk(self):
        raise NotImplementedError

    def detach_disk(self):
        raise NotImplementedError

    def replace_disk(self):
        raise NotImplementedError
