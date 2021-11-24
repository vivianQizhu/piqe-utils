import os
import libvirt
import pytest

from piqe_utils import __loggername__
from piqe_utils.api.logger import PiqeLogger
from piqe_utils.api.utils import get_ssh_connection
from piqe_utils.api.vm_ops.vm_provider.libvirt import libvirt_utils
from piqe_utils.api.vm_ops.vm_provider.libvirt.libvirt_vm import LibvirtVM

logger = PiqeLogger(__loggername__)
remote_session = None
# remote_session = get_ssh_connection(hostname='', username='', password='')


def get_conn():
    conn = libvirt_utils.get_conn()
    return conn


def get_domain():
    conn = get_conn()
    domains = conn.listDomainsID()
    if domains:
        return LibvirtVM(conn.lookupByID(domains[0]).name(), conn)
    else:
        return None


def get_volume_params():
    mod_name = 'libvirt_volume'
    params = libvirt_utils.get_params(mod_name)
    logger.info('Get params for module %s: %s' % (mod_name, str(params)))
    return params


@pytest.fixture(scope="session")
def test_get_conn():
    assert isinstance(get_conn(), libvirt.virConnect)


@pytest.mark.libvirt
def test_get_params():
    assert 'target bus="HDDRIVER"' in get_volume_params()['xml']


@pytest.mark.libvirt
def test_dev_num():
    domain = get_domain()
    if not domain:
        logger.warning("There is no alive domain to be tested, skip testing "
                       "for dev_num()")
    else:
        logger.info('guestname:%s' % domain.domain_name)
        dev_num = libvirt_utils.dev_num(domain.XMLDesc, 'disk')
        assert isinstance(dev_num, int) and dev_num > 0


@pytest.mark.libvirt
def test_create_image():
    disk = '/var/lib/libvirt/images/attacheddisk'
    assert libvirt_utils.create_image(disk, 1, session=remote_session)
    assert os.path.exists(disk)
    assert libvirt_utils.clean_up(disk, session=remote_session)
