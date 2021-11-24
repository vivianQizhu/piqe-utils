"""Module to perform disk related operations on the domain"""
import os
import time

import libvirt

from piqe_utils import __loggername__
from piqe_utils.api import process
from piqe_utils.api import utils
from piqe_utils.api.logger import PiqeLogger
from piqe_utils.api.vm_ops.vm_resource.core import BaseVolume
from . import xml_parser
from . import libvirt_utils


def backup_image(image_path, remote_session):
    """
    Backup image locally

    :param image_path: the path of the image to backup
    :param remote_session: remote ssh session, default None for local cmd
    :return: The path of the backup file or None if failed
    """
    backup_path = '%s.backup' % image_path
    backup_cmd = 'cp %s %s' % (image_path, backup_path)
    if remote_session:
        status = utils.get_status_output_remote(backup_cmd, timeout=None)[0]
    else:
        status = process.getstatusoutput(backup_cmd)[0]
    return backup_path if status == 0 else None


class LibvirtVolume(BaseVolume):
    """
    Define the object for libvirt vm volume, which include the operation of
    certain volume related operations, e.g. attach disk, detach disk, replace
    the disk image.
    """

    def __init__(self, domain, remote_session):
        """
        :param domain: the LibvirtVM object
        :param remote_session: remote ssh session, default None for local cmd
        """
        self.domain = domain
        self.remote_session = remote_session
        self.params = libvirt_utils.get_params(
            str(os.path.basename(__file__)).split('.', maxsplit=1)[0])
        self.hddriver = self.params['hddriver']
        self.xmlstr = self.params['xml']
        self.imagesize = int(self.params.get('imagesize', 1))
        self.imageformat = self.params.get('imageformat', 'raw')
        self.qcow2version = self.params.get('qcow2version', 'v3')
        self.disk = self.params.get('volumepath', '/var/lib/libvirt/images')
        self.disk += "/%s" % self.params.get(
            'volume', '%s_%s' % (self.domain.domain_name, 'attacheddisk'))
        for key, value in self.params.items():
            self.xmlstr = self.xmlstr.replace(key.upper(), str(value))
        self.trash_files = self.disk
        self.logger = PiqeLogger(__loggername__)

    def xml_replace(self, org_str, value):
        """
        Update xmlstr and log it

        :param org_str: the key to be replaced from xmlstr
        :param value: the value desired for the updated xmlstr
        """
        self.xmlstr = self.xmlstr.replace(org_str, value)
        self.logger.info("disk xml:\n%s" % self.xmlstr)

    def get_disk(self, disk_num, next_dev=True):
        """
        Generate last or next new target device name(e.g. vdb/sdc) of the vm

        :param disk_num: The total number of all disks
        :param next: return a new device name if True, and the last one if False
        :return: The target device name
        """
        disk_num = disk_num if next_dev else disk_num - 1
        suffix = chr(ord('a') + disk_num)
        prefix = 'h' if self.hddriver == 'ide' else self.hddriver[0]
        devname = "%sd%s" % (prefix, suffix)
        return devname

    def prepare_image(self, devname):
        """
        Create image file via qemu-img for given device

        :param devname: The name of the device to be operated
        """
        if not self.params.get('volume'):
            self.disk += '_%s' % devname
        self.xmlstr = self.xmlstr.replace('DISKPATH', self.disk)
        self.xml_replace('DEV', devname)
        # Create image, qcow2version includes 'v3', 'v3_lazy_refcounts'
        if not libvirt_utils.create_image(self.disk, self.imagesize,
                                          self.imageformat, self.qcow2version,
                                          self.remote_session):
            self.logger.error("fail to create a image file")

    def attach_disk(self):
        """
        Attach disk to vm, with the pre-processed xml file

        :return: True if attach disk succeed, False otherwise
        """
        disk_num_org = libvirt_utils.dev_num(self.domain.XMLDesc, 'disk')
        self.logger.debug("original disk number: %s" % disk_num_org)
        self.prepare_image(self.get_disk(disk_num_org))
        try:
            # Attach disk to domain
            self.domain.libvirt_domain.attachDevice(self.xmlstr)
            time.sleep(90)
            disk_num_af = libvirt_utils.dev_num(self.domain.XMLDesc, 'disk')
            self.logger.debug("update disk number to %s" % disk_num_af)
            if disk_num_af <= disk_num_org:
                self.logger.error(
                    "fail to attach a disk to guest:\n%s\n" % self.xmlstr)
                return False
        except libvirt.libvirtError as err:
            self.logger.error("API error message: %s" %
                              err.get_error_message())
            return False
        return True

    def detach_disk(self, devname=None):
        """
        Detach disk, for the device name provided or the last disk of the vm

        :param devname: The name of the device to be detached, if not set
                        then detach the last disk of the vm
        :return: True if detach disk succeed, False otherwise
        """
        xml_desc = self.domain.XMLDesc
        xml_par = xml_parser.xml_parser(xml_desc)
        if not devname:
            disk = xml_par.parse()['devices']['disk']
            if isinstance(disk, list):
                disk = disk[-1]
            devname = disk['target']['attr']['dev']
            self.logger.info('Prepare to detach disk: %s' % devname)
        xml_disk = xml_par.get_disk_xml('disk', devname)
        try:
            domain = self.domain.libvirt_domain
            domain.detachDevice(xml_disk)
            # Add sleep to wait detach disk finish
            time.sleep(15)
            if domain.isActive():
                domain.destroy()
                domain.create()
            if devname in self.domain.XMLDesc:
                self.logger.error(
                    "fail to detach a disk from guest:\n%s\n" % self.xmlstr)
                return False
        except libvirt.libvirtError as err:
            self.logger.error("API error message: %s, error code is %s"
                              % (err.get_error_message(), err.get_error_code()))
            return False
        return True

    def _replace_disk(self, xml_disk):
        """
        Stop the domain and replace disk image file with given xml of the disk,
        then start the domain

        :param xml_disk: The xml of the disk to be updated
        """
        domain_alive = False
        domain = self.domain.libvirt_domain
        if domain.isActive():
            domain_alive = True
            domain.destroy()
        domain.updateDeviceFlags(xml_disk,
                                 libvirt.VIR_DOMAIN_DEVICE_MODIFY_FORCE)
        if domain_alive:
            domain.create()

    def replace_disk(self, devname, image_rep,
                     backup=True, rm_image=False):
        """
        Replace disk image file for the given device

        :param devname: The name of the device to be updated
        :param image_rep: The image file desired to update for the disk
        :param backup: To backup the original image file if True
        :param rm_image: To remove the original image file if True
        :return: the backup image path if 'backup' is True, None otherwise
        """
        xml_desc = self.domain.XMLDesc
        xml_par = xml_parser.xml_parser(xml_desc)
        disk = xml_par.get_disk_property(devname)
        if not disk:
            self.logger.error('Does not find disk %s' % devname)
            return False
        image = disk['source']['attr']['file']
        backup_img = None
        if backup:
            backup_img = backup_image(image, self.remote_session)
        if rm_image:
            self.trash_files += ' %s' % image
        xml_disk = xml_par.get_disk_xml('disk', devname)
        xml_disk = xml_disk.replace(image, image_rep)
        self._replace_disk(xml_disk)
        return backup_img

    def clean_up(self):
        """To clean up the trash files"""
        return libvirt_utils.clean_up(self.trash_files, self.remote_session)
