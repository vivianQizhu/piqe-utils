import os
import yaml
import libvirt

from piqe_utils.api import process
from piqe_utils import __loggername__
from piqe_utils.api.logger import PiqeLogger

logger = PiqeLogger(__loggername__)


def get_hypervisor():
    """
    Find proper hypervisor for libvirt connection

    :return: The hypervisor that supported on the host
    """
    cmd = "lsmod | grep kvm"
    if process.getstatusoutput(cmd)[0] == 0:
        return 'kvm'
    elif os.access("/proc/xen", os.R_OK):
        return 'xen'
    else:
        return 'no any hypervisor is running.'


def get_uri(ipaddr):
    """
    Get hypervisor uri

    :param ipaddr: The ipaddr of the host to be connected
    :return: The uri that used to establish the libvirt connection
    """
    hypervisor = get_hypervisor()
    if ipaddr == "127.0.0.1":
        if hypervisor == "xen":
            uri = "xen:///"
        if hypervisor == "kvm":
            uri = "qemu:///system"
    else:
        if hypervisor == "xen":
            uri = "xen+ssh://%s" % ipaddr
        if hypervisor == "kvm":
            uri = "qemu+ssh://%s/system" % ipaddr
    return uri


def request_credentials(credentials, user_data):
    """
    Request credential function for libvirt.openAuth

    :param credentials: libvirt credential type
    :param user_data: The user data containing username and password
    :return: libvirt credential code
    """
    for credential in credentials:
        if credential[0] == libvirt.VIR_CRED_AUTHNAME:
            credential[4] = user_data[0]
            if len(credential[4]) == 0:
                credential[4] = credential[3]
        elif credential[0] == libvirt.VIR_CRED_PASSPHRASE:
            credential[4] = user_data[1]
        else:
            return -1

    return 0


def get_conn(ipaddr='127.0.0.1', username='', password=''):
    """
    Get connection object from libvirt module

    :param ipaddr: The host to establish the connection
    :param username: The username of the host, '' by default
    :param password: The password of the host, '' by default
    :return: The libvirt connection
    """
    uri = get_uri(ipaddr)
    user_data = [username, password]
    auth = [[libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE],
            request_credentials, user_data]
    conn = libvirt.openAuth(uri, auth, 0)
    return conn


def xml_to_string(xml_path):
    """
    Read out xml string from xml file path

    :param xml_path: The xml file path
    :return: The xml string
    """
    if not os.path.isabs(xml_path):
        xml_path = os.path.join('xml', xml_path)
    with open(xml_path, 'r') as file_h:
        text = file_h.read()
    return text


def get_params(mod_name):
    """
    Get parameters for the given module, it should be configured in yaml format
    in './conf/libvirt_conf.yaml', e.g. for module libvirt_volume:
    libvirt_volume:
        xml: 'disk.xml'
        guestname: test
        imageformat: qcow2
        imagesize: 1
        hddriver: virtio

    :param mod_name: The module name
    :return: The parameter dictionary
    """
    conf_path = 'conf/libvirt_conf.yaml'
    cwd = os.path.dirname(__file__)
    logger.info(cwd)
    conf_path = os.path.join(cwd, conf_path)
    conf_file = open(conf_path, 'r', encoding="utf-8")
    conf_data = conf_file.read()
    conf_file.close()
    params = yaml.load(conf_data)
    logger.info('The parameters of module %s: %s' % (mod_name, str(params)))
    params = params[mod_name]
    if 'xml' in params.keys():
        xml_file = params.pop('xml')
        xml_file = (xml_file if os.path.isabs(xml_file) else
                    os.path.join(cwd, 'xml', xml_file))
        with open(xml_file, 'r') as file_h:
            params['xml'] = file_h.read()
    return params


def dev_num(xmlstr, device, xml_prefix='</', xml_suffix='>'):
    """
    Get disk or interface number in the guest
    Return None on FAILURE and the disk/interface number of vm on SUCCESS

    :param xmlstr: The xml description of the vm
    :param device: The device type to be counted
    :param xml_prefix: The xml prefix of the device xml description
    :param xml_suffix: The xml suffix of the device xml description
    :return: The total number of this type of device
    """
    device = xml_prefix + device + xml_suffix
    num = xmlstr.count(device)
    if num:
        return num
    else:
        logger.error("no %s in the domain" % (device))
        return None


def create_image(disk, seeksize, imageformat='raw', qcow2version='v3'):
    """
    Create a image file via qemu-img

    :param disk: The image file to be created
    :param seeksize: The image size to be created
    :param imageformat: The image format, any format supported by qemu-img
    :param qcow2version: The qcow2 version, will add "-o compat=1.1"
                         if it is 'v3'
    :return: True if qemu-img succeed, False otherwise
    """

    if imageformat == 'raw':
        qcow2_options = ""
    elif qcow2version.startswith('v3'):
        qcow2_options = "-o compat=1.1"
        if qcow2version.endswith('lazy_refcounts'):
            qcow2_options = qcow2_options + " -o lazy_refcounts=on"
    cmd = ("qemu-img create -f %s %s %s %sG" %
           (imageformat, qcow2_options, disk, seeksize))
    logger.info("cmd: %s" % cmd)
    s, o = process.getstatusoutput(cmd, shell=True, ignore_status=True)
    if s != 0:
        logger.error(o)
        return False
    return True


def clean_up(trash_list):
    """Cleanup trash files"""
    return process.getstatusoutput('rm -rf %s' % trash_list)[0] == 0