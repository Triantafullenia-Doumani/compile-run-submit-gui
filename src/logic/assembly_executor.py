import os
from PyQt6.QtCore import QThread, pyqtSignal, QProcess, QTimer

class AssemblyExecutor(QThread):
    """
    Executes a RISC-V assembly file using RARS in a separate thread,
    feeding inputs and emitting output to the UI via output_signal.
    """
    output_signal = pyqtSignal(str)

    def __init__(self, asm_file, output_box, inputs=None, parent=None):
        super().__init__(parent)
        self.asm_file = asm_file
        self.inputs = inputs or []
        self.output_box = output_box
        self.process = None

    def run(self):
        # Create QProcess in the thread context.
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)

        # Connect process signals.
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.started.connect(lambda: self.send_inputs(self.process))
        self.process.finished.connect(self._on_finished)
        self.process.errorOccurred.connect(lambda error: None)

        # Build and start the RARS command.
        jar_path = os.path.abspath("src/riscV_simulator/rars_46ab74d.jar")
        self.process.start("java", ["-jar", jar_path, "nc", "sm", self.asm_file])

        if not self.process.waitForStarted():
            self.output_signal.emit("Error: failed to launch RARS.\n")
            return

        # Forcefully kill the process after 3 seconds.
        QTimer.singleShot(3000, self.force_kill)

        # Run the thread's event loop until quit() is called.
        self.exec()

        # Final cleanup in case the process is still running.
        try:
            if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
                self.process.kill()
                self.process.waitForFinished(1000)
        except Exception:
            pass
        try:
            self.process.deleteLater()
        except Exception:
            pass

    def force_kill(self):
        """
        Forcefully kill the process after 3 seconds.
        """
        try:
            if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
                self.process.kill()
                self.process.waitForFinished(1000)
        except Exception:
            pass

    def send_inputs(self, process):
        """Feed input values to the process once it has started."""
        for idx, val in enumerate(self.inputs, start=1):
            self.output_signal.emit(f"Input #{idx}: {val}\n")
            process.write((val + "\n").encode())
            process.waitForBytesWritten()
        # Send an extra newline in case RARS is waiting for a final input.
        process.write("\n".encode())
        process.waitForBytesWritten()
        process.closeWriteChannel()

    def handle_stdout(self):
        """Read and emit process output."""
        try:
            raw = self.process.readAllStandardOutput().data()
            text = raw.decode('utf-8', 'ignore')
            # Clean the text by removing carriage returns or null characters.
            clean = text.replace('\r', '').replace('\x00', '')
            if clean:
                self.output_signal.emit(clean)
        except Exception:
            pass

    def _on_finished(self, exit_code, exit_status):
        """Cleanup after process termination and emit a generic completion message."""
        try:
            self.process.readyReadStandardOutput.disconnect(self.handle_stdout)
            self.process.errorOccurred.disconnect()
            self.process.finished.disconnect(self._on_finished)
        except Exception:
            pass

        self.output_signal.emit("Assembly execution completed.\n")
        self.quit()

    def stop(self):
        """
        Call this method from your UI (e.g., in closeEvent) to ensure the process is
        terminated before the application exits.
        """
        try:
            if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
                self.process.kill()
                self.process.waitForFinished(1000)
        except Exception:
            pass
        self.quit()