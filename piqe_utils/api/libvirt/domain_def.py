"""Module to define a domain object"""

import libvirt
from . import process


def get_hypervisor():
    """Get hypervisor type"""


def get_uri(ipaddr):
    """Get hypervisor uri"""

    return uri


def get_conn(uri='', username='', password=''):
    """ get connection object from libvirt module
    """

    return conn


class Domain(object):
    """
    Define the object Domain
    """
    def __init__(self, domain_name):
        self.domain_name = domain_name
        self.conn = get_conn()
        self.dom = self.conn.lookupByName(domain_name)
        self.info = dom.info()
        self.domxml = dom.XMLDesc(0)
