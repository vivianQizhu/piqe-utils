import inspect
from .vm_resource.core import BaseVM, BaseVolume
from .vm_provider.libvirt import libvirt_vm, libvirt_volume


class VM(object):
    """The basic definition of the object VM"""

    def __init__(self, provider='libvirt', **kwargs):
        target_module = eval('%s_vm' % provider)
        module_cls = inspect.getmembers(target_module, inspect.isclass)
        try:
            target_cls = [i[1] for i in module_cls if issubclass(i[1], BaseVM)
                          and i[1] is not BaseVM][0]
            self.vm_cls = target_cls(**kwargs)
            self.__dict__.update(self.vm_cls.__dict__.copy())
        except IndexError:
            raise NotImplementedError()

    def reboot(self, **kwargs):
        if hasattr(self.vm_cls, 'reboot'):
            self.vm_cls.reboot(**kwargs)
        else:
            raise NotImplementedError()

    def graceful_shutdown(self, **kwargs):
        if hasattr(self.vm_cls, 'graceful_shutdown'):
            self.vm_cls.graceful_shutdown(**kwargs)
        else:
            raise NotImplementedError()


class Volume(object):

    def __init__(self, provider='libvirt', **kwargs):
        target_module = eval('%s_volume' % provider)
        module_cls = inspect.getmembers(target_module, inspect.isclass)
        try:
            target_cls = [i[1] for i in module_cls if issubclass(
                i[1], BaseVolume) and i[1] is not BaseVolume][0]
            self.volume_cls = target_cls(**kwargs)
            self.__dict__.update(self.volume_cls.__dict__.copy())
        except IndexError:
            raise NotImplementedError()

    def get_disk(self, **kwargs):
        if hasattr(self.volume_cls, 'get_disk'):
            return self.volume_cls.get_disk(**kwargs)
        else:
            raise NotImplementedError()

    def attach_disk(self, **kwargs):
        if hasattr(self.volume_cls, 'attach_disk'):
            return self.volume_cls.attach_disk(**kwargs)
        else:
            raise NotImplementedError()

    def detach_disk(self, **kwargs):
        if hasattr(self.volume_cls, 'detach_disk'):
            return self.volume_cls.detach_disk(**kwargs)
        else:
            raise NotImplementedError()

    def replace_disk(self, **kwargs):
        if hasattr(self.volume_cls, 'replace_disk'):
            return self.volume_cls.replace_disk(**kwargs)
        else:
            raise NotImplementedError()
