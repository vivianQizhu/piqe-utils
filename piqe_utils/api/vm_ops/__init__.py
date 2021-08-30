import inspect
from .vm_resource.core import BaseVM, BaseVolume
from .vm_provider.libvirt import libvirt_vm, libvirt_volume


class VM(object):
    """The basic definition of the object VM"""

    def __init__(self, provider='libvirt', **kargs):
        target_module = eval('%s_vm' % provider)
        module_cls = inspect.getmembers(target_module, inspect.isclass)
        try:
            target_cls = [i[1] for i in module_cls if issubclass(i[1], BaseVM)
                          and i[1] is not BaseVM][0]
            self.vm_cls = eval(target_cls)(**kargs)
        except IndexError:
            raise NotImplementedError()

    def reboot(self):
        if hasattr(self.vm_cls, 'reboot'):
            self.vm_cls.reboot()
        else:
            raise NotImplementedError()

    def graceful_shutdown(self):
        if hasattr(self.vm_cls, 'graceful_shutdown'):
            self.vm_cls.graceful_shutdown()
        else:
            raise NotImplementedError()


class Volume(object):

    def __init__(self, provider='libvirt', **kargs):
        target_module = eval('%s_volumn' % provider)
        module_cls = inspect.getmembers(target_module, inspect.isclass)
        try:
            target_cls = [i[1] for i in module_cls if issubclass(
                i[1], BaseVolume) and i[1] is not BaseVolume][0]
            self.vm_cls = eval(target_cls)(**kargs)
        except IndexError:
            raise NotImplementedError()

    def get_disk(self):
        if hasattr(self.volume_cls, 'get_disk'):
            self.volume_cls.get_disk()
        else:
            raise NotImplementedError()

    def attach_disk(self):
        if hasattr(self.volume_cls, 'attach_disk'):
            self.volume_cls.attach_disk()
        else:
            raise NotImplementedError()

    def detach_disk(self):
        if hasattr(self.volume_cls, 'detach_disk'):
            self.volume_cls.detach_disk()
        else:
            raise NotImplementedError()

    def replace_disk(self):
        if hasattr(self.volume_cls, 'replace_disk'):
            self.volume_cls.replace_disk()
        else:
            raise NotImplementedError()
