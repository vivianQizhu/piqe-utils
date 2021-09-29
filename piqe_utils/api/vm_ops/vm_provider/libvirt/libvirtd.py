"""Module to perform libvirtd related operations"""

from paramiko import SSHClient
from piqe_utils.api.utils import get_output_local, get_output_remote

SERVICE_NAME = "libvirtd.service"

class Libvirtd():
    """
    Class to manage libvirtd service on hosts.
    """
    def __init__(self,conn=None):
        """
        Init libvirtd obj
        :param SSHClient conn:the conneciton object of SSHClient
            if None == conne,localhost libvirtd service will be
        managed
        """
        if conn and isinstance(conn,SSHClient):
            self.ssh_conn = conn
        else:
            self.ssh_conn = None

    def run_cmd(self,cmd,timeout=60):
        """
        run cmd from local or remote
        """
        if self.ssh_conn:
            return get_output_remote(self.ssh_conn,cmd,timeout)
        return get_output_local(cmd,timeout)

    def _is_modules_enabled(self):
        cmd = f"""
        systemctl list-unit-files --no-pager | \
        grep {SERVICE_NAME} | \
        awk '{{print $NF}}'
        """
        out_info,_ = self.run_cmd(cmd)
        if "enabled" in out_info:
            return False
        return True

    def start(self,timeout=60):
        """
        Start libvirtd service
        """
        cmd = f"systemctl start {SERVICE_NAME}"
        out_info,err_info = self.run_cmd(cmd,timeout)
        if len(err_info) > 0:
            print(err_info)
            return False
        print(out_info)
        return True

    def stop(self,timeout=60):
        """
        Stop libvirtd service
        """
        cmd = f"""
        systemctl stop libvirtd-admin.socket
        systemctl stop libvirtd-ro.socket
        systemctl stop libvirtd.socket
        systemctl stop {SERVICE_NAME}
        """
        out_info,err_info = self.run_cmd(cmd,timeout)
        if len(err_info) > 0:
            print(err_info)
            return False
        print(out_info)
        return True

    def restart(self,timeout=60):
        """
        Restart libvirtd service
        """
        cmd = f"systemctl restart {SERVICE_NAME}"
        out_info,err_info = self.run_cmd(cmd,timeout)
        if len(err_info) > 0:
            print(err_info)
            return False
        print(out_info)
        return True

    def is_running(self,timeout=60):
        """
        Check whether libvirtd is running
        """
        cmd = f"systemctl status {SERVICE_NAME}"
        out_info,err_info = self.run_cmd(cmd,timeout)
        if len(err_info) > 0:
            print(err_info)
            return False
        print(out_info)
        if "Active: active" in out_info:
            print("Active")
            return True
        return False

if __name__ == "__main__":
    # ssh_conn = get_ssh_connection(
    #     hostname="",
    #     username="",
    #     password="")
    # print("remtoe test begin")
    # o_libvirt = Libvirtd(ssh_conn)
    # o_libvirt.start()
    # o_libvirt.is_running()
    # o_libvirt.stop()
    # o_libvirt.is_running()
    # o_libvirt.restart()
    # o_libvirt.is_running()
    # print("remtoe test end")
    # print("local test begin")
    # o_local = Libvirtd()
    # o_local.start()
    # o_local.is_running()
    # o_local.stop()
    # o_local.is_running()
    # o_local.restart()
    # o_local.is_running()
    # print("local test end")
    # print(o_local._is_modules_enabled())
    # o_local.start()
    pass
