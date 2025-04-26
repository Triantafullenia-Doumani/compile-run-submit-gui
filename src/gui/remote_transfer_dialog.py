import socket
import time
import logging
import paramiko
from paramiko import SSHClient, AutoAddPolicy, Transport
from paramiko.ssh_exception import BadAuthenticationType, SSHException, AuthenticationException
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QLabel,
    QDialogButtonBox, QMessageBox
)

# enable debug logging for Paramiko
paramiko.util.log_to_file("paramiko.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AuthWorker(QThread):
    success = pyqtSignal(tuple)
    failure = pyqtSignal(str)

    def __init__(self, server, username, password):
        super().__init__()
        self.server = server
        self.username = username
        self.password = password

    def run(self):
        # Try password auth first
        fallback = False
        for attempt in range(1, 4):
            ssh = SSHClient()
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            try:
                ssh.connect(
                    self.server,
                    username=self.username,
                    password=self.password,
                    timeout=10,
                    allow_agent=False,
                    look_for_keys=False,
                    banner_timeout=10,
                    auth_timeout=10
                )
                stdin, stdout, _ = ssh.exec_command("whoami")
                result = stdout.read().decode().strip().lower()
                if result == self.username.lower():
                    self.success.emit((self.username, self.password))
                    return
                else:
                    self.failure.emit("Authenticated but unable to verify user.")
                    return
            except BadAuthenticationType as e:
                if "keyboard-interactive" in e.allowed_types:
                    fallback = True
                    break
                self.failure.emit("No supported auth methods.")
                return
            except AuthenticationException:
                self.failure.emit("Invalid username or password.")
                return
            except SSHException as e:
                if "No existing session" in str(e):
                    fallback = True
                    break
                logger.error("SSH error during password auth: %s", e)
                self.failure.emit(f"SSH error: {e}")
                return
            finally:
                ssh.close()
            time.sleep(2)

        if not fallback:
            self.failure.emit("Authentication methods not supported.")
            return

        # Keyboard-interactive fallback
        for attempt in range(1, 4):
            sock = None
            transport = None
            try:
                sock = socket.create_connection((self.server, 22), timeout=10)
                transport = Transport(sock)
                transport.start_client(timeout=10)
                transport.auth_interactive(
                    self.username,
                    lambda title, instr, prompts: [self.password] * len(prompts)
                )
                chan = transport.open_session()
                chan.exec_command("whoami")
                out = chan.recv(1024).decode().strip().lower()
                if out == self.username.lower():
                    self.success.emit((self.username, self.password))
                    return
            except SSHException as e:
                logger.warning("Interactive auth attempt %d failed: %s", attempt, e)
                time.sleep(2)
            finally:
                if transport:
                    transport.close()
                if sock:
                    sock.close()

        self.failure.emit("Keyboard-interactive authentication failed.")

class RemoteTransferDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.server = "scylla.cs.uoi.gr"
        self.setWindowTitle("Remote File Transfer Login")
        self.setObjectName("remoteTransferDialog")

        layout = QFormLayout(self)
        self.usernameLabel = QLabel("Username:", self)
        self.username_field = QLineEdit(self)
        layout.addRow(self.usernameLabel, self.username_field)

        self.passwordLabel = QLabel("Password:", self)
        self.password_field = QLineEdit(self)
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow(self.passwordLabel, self.password_field)

        self.infoLabel = QLabel(f"Server: {self.server}", self)
        layout.addRow(self.infoLabel)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel,
            self
        )
        buttons.accepted.connect(self.handle_accept)
        buttons.rejected.connect(self.handle_reject)
        layout.addWidget(buttons)

        self._credentials = None
        self.auth_thread = None

    def handle_accept(self):
        user = self.username_field.text().strip()
        pwd = self.password_field.text().strip()
        if not user or not pwd:
            QMessageBox.warning(self, "Input Error", "Username and password cannot be empty.")
            return
        self.username_field.setEnabled(False)
        self.password_field.setEnabled(False)
        self.auth_thread = AuthWorker(self.server, user, pwd)
        self.auth_thread.success.connect(self.on_auth_success)
        self.auth_thread.failure.connect(self.on_auth_failure)
        self.auth_thread.start()

    def on_auth_success(self, creds):
        self._credentials = creds
        self.clear_fields()
        super().accept()

    def on_auth_failure(self, message):
        QMessageBox.critical(self, "Authentication Failed", message)
        self.clear_fields()
        super().reject()

    def handle_reject(self):
        self.clear_fields()
        super().reject()

    def clear_fields(self):
        self.username_field.clear()
        self.password_field.clear()
        self.username_field.setEnabled(True)
        self.password_field.setEnabled(True)

    def get_credentials(self):
        return self._credentials
