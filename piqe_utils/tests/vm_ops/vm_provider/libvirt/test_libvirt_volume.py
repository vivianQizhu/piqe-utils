import pytest

from piqe_utils.api.vm_ops.vm_provider.libvirt import libvirt_utils
from piqe_utils.api.vm_ops.vm_provider.libvirt.libvirt_vm import LibvirtVM
from piqe_utils.api.vm_ops.vm_provider.libvirt.libvirt_volume import LibvirtVolume
from piqe_utils import __loggername__
from piqe_utils.api.logger import PiqeLogger

logger = PiqeLogger(__loggername__)


@pytest.fixture(scope="class")
def volume_obj():
    conn = libvirt_utils.get_conn()
    try:
        dom = LibvirtVM(conn.lookupByID(conn.listDomainsID()[0]).name(), conn)
    except IndexError:
        logger.error('There is no active domain to be tested.')
        raise
    return LibvirtVolume(dom)


@pytest.mark.libvirt
class TestLibvirtVolume(object):

    def test_get_disk(self, volume_obj):
        assert volume_obj.get_disk(2) == 'vdc'
        assert volume_obj.get_disk(1, next=False) == 'vda'

    def test_disk_attach_detach(self, volume_obj):
        assert volume_obj.attach_disk()
        assert volume_obj.detach_disk()

    def test_replace_disk(self, volume_obj):
        backup_image = volume_obj.backup_image(volume_obj.disk)
        disk = volume_obj.get_disk(1, next=False)
        backup = volume_obj.replace_disk(disk, backup_image)
        domain = volume_obj.domain.libvirt_domain
        assert backup_image in domain.XMLDesc()
        assert domain.isActive()
        assert volume_obj.replace_disk(disk, backup, backup=True, rm_image=True)
        libvirt_utils.clean_up(backup_image)

    def test_clean_up(self, volume_obj):
        assert volume_obj.clean_up()
