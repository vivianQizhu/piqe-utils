"""
Module for utils
"""
import subprocess as sp
import paramiko

SSH_PORT = 22

def get_ssh_connection(
    hostname,
    port=SSH_PORT,
    username=None,
    password=None,
    pkey=None,
    key_filename=None,
    ):
    """
    Get ssh connection
    :param str hostname: the server to connect to
    None means localhost
    :param int port: the server port to connect to
    :param str username:
        the username to authenticate as (defaults to the current local
        username)
    :param str password:Used for password authentication
    Authentication is attempted in the following order of priority:

        - The ``pkey`` or ``key_filename`` passed in (if any)

            - ``key_filename`` may contain OpenSSH public certificate paths
            as well as regular private-key paths; when files ending in
            ``-cert.pub`` are found, they are assumed to match a private
            key, and both components will be loaded. (The private key
            itself does *not* need to be listed in ``key_filename`` for
            this to occur - *just* the certificate.)

        - Any key we can find through an SSH agent
        - Any "id_rsa", "id_dsa" or "id_ecdsa" key discoverable in
            ``~/.ssh/``

            - When OpenSSH-style public certificates exist that match an
            existing such private key (so e.g. one has ``id_rsa`` and
            ``id_rsa-cert.pub``) the certificate will be loaded alongside
            the private key and used for authentication.

        - Plain username/password auth, if a password was given
    :raises:
        `.BadHostKeyException` -- if the server's host key could not be
        verified
        :raises: `.AuthenticationException` -- if authentication failed
        :raises:
        `.SSHException` -- if there was any other error connecting or
        establishing an SSH session
        :raises socket.error: if a socket error occurred while connecting
    """
    if hostname is None:
        return None
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname,
        port,
        username=username,
        password=password,
        pkey=pkey,
        key_filename=key_filename)
    return client

def close_ssh_connection(conn):
    """
    Close the ssh connection
    :param SSHClient conn:
        the conneciton object of SSHClient
    """
    if conn and isinstance(conn,paramiko.SSHClient):
        conn.close()


def get_output_remote(conn,cmd,timeout=60):
    """
    Get cmd running on remote output
    """
    if conn and isinstance(conn,paramiko.SSHClient):
        _,out,err = conn.exec_command(cmd,timeout=timeout)
        err_info = err.read().decode().strip()
        out_info = out.read().decode().strip()
        return out_info,err_info
    return None,None

def get_output_local(cmd,timeout=60):
    """
    Get cmd running on local output
    """
    sp_obj = sp.Popen(cmd,stdout=sp.PIPE,stderr=sp.PIPE,shell=True)
    out,err = sp_obj.communicate(timeout=timeout)
    err_info = err.decode().strip()
    out_info = out.decode().strip()
    return out_info,err_info
