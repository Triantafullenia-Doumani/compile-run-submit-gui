from PyQt6.QtCore import QProcess, pyqtSignal, QObject, QTimer
from PyQt6.QtWidgets import QInputDialog

class CExecutor(QObject):
    output_signal = pyqtSignal(str)

    def __init__(self, executable_path, output_box, input_names=None, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.executable_path = executable_path
        self.output_box = output_box
        self.input_names = input_names or []
        self.input_index = 0
        self.expecting_input = True

        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.started.connect(self.on_started)
        self.process.finished.connect(self.on_finished)

    def start(self):
        self.process.start(self.executable_path)

    def on_started(self):
        self.output_signal.emit("C process started.\n")
        QTimer.singleShot(200, self.send_next_input)

    def on_finished(self, exitCode, exitStatus):
        self.expecting_input = False
        self.output_signal.emit(f"Intermediate code execution completed successfully")

    def send_next_input(self):
        if self.input_index < len(self.input_names) and self.expecting_input:
            name = self.input_names[self.input_index]
            value, ok = QInputDialog.getText(None, "Input Required", f"Enter value for {name}:")
            if ok:
                self.send_input(value)
                self.input_index += 1
                QTimer.singleShot(200, self.send_next_input)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        text = data.data().decode('utf-8')
        self.output_signal.emit(text)

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        text = data.data().decode('utf-8')
        self.output_signal.emit(text)

    def send_input(self, text):
        if not text.endswith('\n'):
            text += '\n'
        self.process.write(text.encode('utf-8'))
