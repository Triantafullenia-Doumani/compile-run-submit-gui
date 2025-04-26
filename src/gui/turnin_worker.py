from PyQt6.QtCore import QThread, pyqtSignal
from src.logic.submit_files import execute_remote_turnin

class TurninWorker(QThread):
    finished = pyqtSignal(str, str)  

    def __init__(
        self,
        username: str,
        password: str,
        file_loader: dict[str, str],
        assignment: str,
        course: str,
        host: str
    ):
        super().__init__()
        self.username = username
        self.password = password
        self.file_loader = file_loader
        self.assignment = assignment
        self.course = course
        self.host = host

    def run(self):
        try:
            out, err = execute_remote_turnin(
                self.username,
                self.password,
                self.file_loader,
                self.assignment,
                self.course,
                self.host
            )
        except Exception as e:
            out, err = "", f"Remote submission error: {e!r}"
        self.finished.emit(out, err)
