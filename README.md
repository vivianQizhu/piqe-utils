# piqe-utils
piqe utils contains common libs necessary for piqe 

## Setup

### Package denpendency

    $ sudo dnf install libvirt libvirt-devel python3-devel

Switch to virtualenv

    $ sudo pip3 install virtenv
    $ python3 -m venv venv
    $ source venv/bin/activate

### Requirements
    $ pip3 install pytest libvirt-python pyyaml

### Installation
    $ python3 setup.py install

### Usage

    This repo is aim to provide utils, and this section introuduces the usage of common functions:

#### vm_ops

     The class VM, Volume provide common api for VM operations and VM Volume operations, calling child class for BaseVM and BaseVolumn per the parameters pass to it.

```
    from piqe_utils.api.vm_ops import VM
    from piqe_utils.api.vm_ops, import Volume
    from piqe_utils.api.vm_ops.vm_provider.libvirt import libvirt_utils

    conn = libvirt_utils.get_conn()
    dom_list = conn.listDomainsID()
    vm_kwargs = {'domain_name': conn.lookupByID(dom_list[0]).name(),
                 'conn': conn}
    vm = VM(provider='libvirt', vm_kwargs)
    kwargs = {'domain': vm}
    vm_volumn = vm_ops.Volume('libvirt', **kwargs)
    kwargs = {'disk_num': 1, 'next_dev': False}
    vm_volumn.get_disk(**kwargs)
    # To attach/detach a disk, the attached disk xml should be defined at
    # vm_provider/libvirt/xml/disk.xml, and the related options should be
    # defined at vm_provider/libvirt/conf/libvirt_conf.yaml
    vm_volumn.attach_disk()
    vm_volumn.detach_disk() # could provide devname or keep default then the last disk, the vm will be reboot to check the updated xml
    # To replace a disk image, provide the devname and the image file to replace
    kwargs = {'devname': disk, 'image_rep': backup_image}
    backup = volume_obj.replace_disk(**kwargs) # Note that the vm will be reboot
```

#### vm_resource.core

     The class BaseVM, BaseVolume:
     Abstract for common VM/VM Volunm definition, should not be called directly. When there is new VM type, it should be inherited from these classes

#### vm_provider.libvirt

	It provides the general utils and operations of libvirt vm, and it works like below: 

```
    from piqe_utils.api.vm_ops.vm_provider.libvirt import libvirt_utils
    from piqe_utils.api.vm_ops.vm_provider.libvirt.libvirt_vm import LibvirtVM
    from piqe_utils.api.vm_ops.vm_provider.libvirt.libvirt_volume import LibvirtVolume
        
    conn = libvirt_utils.get_conn()
    dom_list = conn.listDomainsID()
    dom = LibvirtVM(conn.lookupByID(dom_list[0]).name(), conn)
    volume_obj = LibvirtVolume(dom)
    # To attach/detach a disk, the attached disk xml should be defined at 
    # vm_provider/libvirt/xml/disk.xml, and the related options should be
    # defined at vm_provider/libvirt/conf/libvirt_conf.yaml
    volume_obj.attach_disk()
    volume_obj.detach_disk() # could provide devname or keep default then the last disk, the vm will be reboot to check the updated xml
    # To backup a image for the disk, provide the devname
    backup_image = volume_obj.backup_image(volume_obj.disk)
    # To replace a disk image, provide the devname and the image file to replace
    backup = volume_obj.replace_disk(disk, backup_image) # Note that the vm will be reboot
    # To clean the enviroment after testing
    volume_obj.clean_up()
```
	For more details please check pytest test cases test_libvirt_utils and test_libvirt_volumn under tests.vm_ops.vm_provider.libvirt

