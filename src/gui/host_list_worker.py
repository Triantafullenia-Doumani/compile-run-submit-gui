from PyQt6.QtCore import QThread, pyqtSignal
from src.logic.submit_files import get_online_lab_hosts

class HostListWorker(QThread):
    hosts_ready = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, username: str, password: str):
        super().__init__()
        self.username = username
        self.password = password

    def run(self):
        try:
            hosts = get_online_lab_hosts(self.username, self.password)
            self.hosts_ready.emit(hosts)
        except Exception as e:
            self.error.emit(str(e))
