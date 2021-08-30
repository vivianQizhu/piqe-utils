#!/usr/bin/env python
#
# xml_parser.py: Parse XML document, the result is a python dict.
#
# Copyright (C) 2010-2012 Red Hat, Inc.
#
# libvirt-test-API is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranties of
# TITLE, NON-INFRINGEMENT, MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import types

from xml.dom import minidom

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class xml_parser(object):

    """Class xml_parser. It parses and xml document into a python dictionary.
       The elements of the xml documents will be python dictionary keys. For
       example, the xml document:
          <firstel>firstdata</firstel>
          <secondel>
              <subinsecond> seconddata </subinsecond>
          </secondel>
       will be parsed into the python dictionary:
         { "firstel":"firstdata" , "secondel":{"subsinsecond":"seconddata"} }
       Then the data can be retrieve as:
       out = xml_parser.xml_parser().parse(xml)
       out["firstel"] (this will be firstdata )
       out["secondel"]["subinsecond"] (this will be seconddata)

       attributes will be put into attr hash, so say the xml document is:
       <source>
         <device path = '/dev/mapper/vg_hpdl120g501-lv_home'/>
       </source>

       It will be parsed into:
       out["source"]["device"]["attr"]["path"]
       which will be set to:
         "/dev/mapper/vg_hpdl120g501-lv_home"
    """

    def __init__(self, xml_obj):
        """
        Generate minidom Node object for the given xml
        :param xml_obj: The xml file or xml string, generate
                        StringIO for it if it is string
        """
        self.root_node = None
        if sys.version_info[0] >= 3:
            from io import IOBase
            filetype = IOBase
        else:
            filetype = types.FileType
        filepath = xml_obj
        if not isinstance(filepath, filetype):
            if os.path.exists(filepath):
                print("file: %s " % xml_obj)
            else:
                filepath = StringIO(xml_obj)
        xmldoc = minidom.parse(filepath)
        self.root_node = xmldoc.firstChild

    def parse(self):
        """Parse into a dictionary for the xml object"""
        outdic = dict()
        self.parseintodict(self.root_node, 0, outdic)
        return outdic

    def parseintodict(self, node, level, out, rootkey=None):
        """
        Parse into dictionary for given node

        :param node: minidom.Node type object
        :param level: The level to iterate
        :param out: the output dictionary
        :param rootkey: The rootkey to be set, to integrate nodes with same key
        """
        for thenode in node.childNodes:
            if thenode.nodeType == node.ELEMENT_NODE:
                key = thenode.nodeName
                try:
                    value = thenode.childNodes[0].data
                    if value.strip() == '':
                        value = None
                except Exception:
                    value = None
                newdict = {key: value}
                attrdic = None
                if rootkey is not None:
                    self.keyfindandset(out, rootkey, thenode)
                else:
                    if thenode.attributes is not None:
                        tmpattr = dict()
                        if thenode.attributes.length > 0:
                            for attrkey in list(thenode.attributes.keys()):
                                tmpattr.update(
                                    {attrkey: thenode.attributes.get(attrkey).nodeValue})
                            attrdic = {"attr": tmpattr}
                    if key in out:
                        if out[key] is None:
                            if attrdic is not None:
                                if value is None:
                                    out[key] = attrdic
                                else:
                                    valdic = {"value": value}
                                    valdic.update(attrdic)
                                    out[key] = valdic
                            else:
                                out[key] = value
                        elif type(out[key]) == list:
                            if attrdic is not None:
                                newdict.update(attrdic)
                            out[key].append(newdict)
                        elif type(out[key]) == dict:
                            if attrdic is not None:
                                newdict.update(attrdic)
                            out[key].update(newdict)
                        else:
                            tmp = out[key]
                            out[key] = [tmp, value]
                    else:
                        out[key] = value
                        if attrdic is not None:
                            if value is None:
                                newdict[key] = attrdic
                            else:
                                valdic = {"value": value}
                                valdic.update(attrdic)
                                newdict = valdic
                            out[key] = newdict
                self.parseintodict(thenode, level+1, out, key)
        return out

    def keyfindandset(self, thedict, thekey, thenode):
        """
        Find existed key and set it, to integrate different definitions(nodes)
         for the same object together

        :param thedict: The whole dictionary to be processed
        :param thekey: The key to be found and set
        :param thenode: The node waiting to be updated into the dictionary
        """
        # get the key/value pair from the node.
        newvalkey = thenode.nodeName
        try:
            value = thenode.childNodes[0].data
            if value.strip() == '':
                value = None
        except Exception:
            value = None
        newval = {newvalkey: value}
        attrdic = None
        if thenode.attributes is not None:
            tmpattr = dict()
            if thenode.attributes.length > 0:
                for key in list(thenode.attributes.keys()):
                    tmpattr.update(
                        {key: thenode.attributes.get(key).nodeValue})
                attrdic = {"attr": tmpattr}
        if attrdic is not None:
            if value is None:
                newval.update({newvalkey: attrdic})
            else:
                valdic = {"value": value}
                newval.update(valdic)
                newval.update(attrdic)
        for key in list(thedict.keys()):
            if key == thekey:
                if type(thedict[key]) == dict:
                    if newvalkey in thedict[key]:
                        if type(thedict[key][newvalkey]) is not list:
                            thedict[key][newvalkey] = [thedict[key][newvalkey]]
                        if newval[newvalkey] is not None:
                            thedict[key][newvalkey].append(newval[newvalkey])
                        else:
                            thedict[key][newvalkey].append(dict())
                    else:
                        thedict[key].update(newval)
                elif type(thedict[key]) == list:
                    if newvalkey in thedict[key][-1]:
                        thedict[key].append(newval)
                    else:
                        thedict[key][-1].update(newval)
                else:
                    thedict[key] = newval
            if type(thedict[key]) == dict:
                self.keyfindandset(thedict[key], thekey, thenode)

    def get_disk_xml(self, device='disk', device_name=None):
        """
        Get disk xml description for given device

        :param device: The device type, 'disk' by default
        :param device_name: The device name desired
        :return: The xml string of the device
        """
        all_devices = self.root_node.getElementsByTagName('devices')[0]
        target_devices = all_devices.getElementsByTagName(device)
        if not device_name:
            return target_devices.toxml()
        try:
            for device in target_devices:
                if device.getElementsByTagName('target')[0].attributes.get(
                        'dev').nodeValue == device_name:
                    return device.toxml()
        except Exception:
            return None
        return None

    def get_disk_property(self, devname):
        """
        Parse the disk's xml description into dictionary

        :param devname: The device name of the disk
        :return: The dictionary parse from the disk's xml description
        """
        disks = self.parse()['devices']['disk']
        if type(disks) is not list:
            disks = [disks]
        for disk in disks:
            if disk['target']['attr']['dev'] == devname:
                return disk
        return None
