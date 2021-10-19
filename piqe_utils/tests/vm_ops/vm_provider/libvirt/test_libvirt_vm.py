import os
import libvirt
import pytest

from piqe_utils import __loggername__
from piqe_utils.api.logger import PiqeLogger
from piqe_utils.api.vm_ops.vm_provider.libvirt import libvirt_utils
from piqe_utils.api.vm_ops.vm_provider.libvirt.libvirt_vm import LibvirtVM

logger = PiqeLogger(__loggername__)


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


@pytest.mark.libvirt
def test_reboot_vm():
    domain = get_domain()
    if not domain:
        logger.warning("There is no alive domain to be tested, skip testing "
                       "for dev_num()")
    else:
        logger.info('guestname:%s' % domain.domain_name)
        ret = domain.reboot()
        assert ret == 0

@pytest.mark.libvirt
def test_shutdown_vm():
    domain = get_domain()
    if not domain:
        logger.warning("There is no alive domain to be tested, skip testing "
                       "for dev_num()")
    else:
        logger.info('guestname:%s' % domain.domain_name)
        ret = domain.graceful_shutdown()
        assert ret == 0
