import os
import shlex
import re
import time
import logging
import socket
import paramiko
from paramiko import SSHClient, AutoAddPolicy, Transport, SFTPClient
from paramiko.ssh_exception import BadAuthenticationType, SSHException, AuthenticationException

# enable debug logging for Paramiko
paramiko.util.log_to_file("paramiko.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)

ANSI_CSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")

def strip_ansi(s: str) -> str:
    return ANSI_CSI_RE.sub("", s)


def get_online_lab_hosts(username, password):
    """
    Connect to scylla.cs.uoi.gr and run 'rupt' to retrieve a list of online lab workstations.
    """
    server = "scylla.cs.uoi.gr"
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(server, username=username, password=password, timeout=10)
        stdin, stdout, stderr = client.exec_command("rupt", get_pty=True)
        rupt_output = stdout.read().decode()
    finally:
        client.close()

    hosts = []
    for line in rupt_output.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1].lower() == "up":
            hosts.append(parts[0])
    return hosts

def execute_remote_turnin(username, password, file_loader, assignment, course, selected_host):
    """
    1) SFTP-upload each file to scylla home dir.
    2) Open an interactive shell, ssh into selected_host, handle password prompts,
       then send 'turnin assignment@course <files>' and collect its output.
    """
    server = "scylla.cs.uoi.gr"
    # upload via SFTP
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(server, username=username, password=password, timeout=10)
        sftp = client.open_sftp()
        for _, path in file_loader.items():
            sftp.put(path, os.path.basename(path))
        sftp.close()

        chan = client.invoke_shell()
        output = ""

        # 1) ssh into jump host
        chan.send(f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {selected_host}\n")
        start = time.time()
        attempts = 0
        while time.time() - start < 30:
            if chan.recv_ready():
                data = chan.recv(1024).decode()
                output += data
                if "password:" in data.lower() or "permission denied" in data.lower():
                    if attempts < 3:
                        chan.send(password + "\n")
                        attempts += 1
                if ("$" in data or "#" in data) and attempts > 0:
                    break
            time.sleep(0.5)

        # 2) run turnin
        files = " ".join(shlex.quote(os.path.basename(p)) for p in file_loader.values())
        cmd = f"turnin {assignment}@{course} {files}\n"
        chan.send(cmd)

        last = time.time()
        while True:
            if chan.recv_ready():
                data = chan.recv(1024).decode()
                output += data
                last = time.time()
                if "do you want" in data.lower() or "please enter" in data.lower():
                    chan.send("y\n")
            else:
                if time.time() - last > 5:
                    break
                time.sleep(0.5)

        chan.send("exit\n")
        time.sleep(1)
        while chan.recv_ready():
            output += chan.recv(1024).decode()

        return output, ""
    except Exception as e:
        return "", f"Remote turnin failed: {e}"
    finally:
        try: client.close()
        except: pass






 