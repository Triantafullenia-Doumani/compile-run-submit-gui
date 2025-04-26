from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QDialogButtonBox, QFileDialog, QWidget, QHBoxLayout,
    QPlainTextEdit
)
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import Qt, QUrl
import os

class ConfirmSubmissionDialog(QDialog):
    def __init__(self, file_loader: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Submission")
        self.resize(500, 350)
        # copy initial files
        self.files = dict(file_loader)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Are you sure you want to submit these files?\n" 
        ))

        # the list of files with "X" buttons
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.open_file_preview)
        layout.addWidget(self.list_widget)

        # Browse button to add more files
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self.browse_files)
        layout.addWidget(btn_browse)

        # populate initial list (won't attempt to toggle Next yet)
        self._refresh_list()

        # Next / Cancel buttons
        button_box = QDialogButtonBox(self)
        self.next_btn = button_box.addButton(
            "Next", QDialogButtonBox.ButtonRole.AcceptRole
        )
        cancel_btn = button_box.addButton(
            "Cancel", QDialogButtonBox.ButtonRole.RejectRole
        )
        self.next_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(button_box)

        # initial enable/disable of Next
        self.update_next_button()

    def _refresh_list(self):
        """Rebuild the QListWidget items from self.files."""
        self.list_widget.clear()
        for key, path in self.files.items():
            # human-readable size
            if os.path.exists(path):
                size = os.path.getsize(path)
                hr = self.human_readable_size(size)
            else:
                hr = "Unknown size"
            text = f"{os.path.basename(path)} ({hr})"

            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, key)

            widget = QWidget()
            h = QHBoxLayout(widget)
            h.setContentsMargins(0, 0, 0, 0)
            h.addWidget(QLabel(text))

            btn_x = QPushButton("X")
            btn_x.setObjectName("removeButton")
            btn_x.setFixedWidth(24)
            btn_x.clicked.connect(lambda _, it=item: self._remove_item(it))
            h.addWidget(btn_x)

            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

        # after list changes, update Next button if it exists
        if hasattr(self, 'next_btn'):
            self.next_btn.setEnabled(bool(self.files))

    def _remove_item(self, item: QListWidgetItem):
        """Remove the selected file from self.files and refresh."""
        key = item.data(Qt.ItemDataRole.UserRole)
        if key in self.files:
            del self.files[key]
        self._refresh_list()

    def browse_files(self):
        """Allow the user to add more files to submit."""
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Add more files", "", "All Files (*)"
        )
        for p in paths:
            self.files[p] = p
        self._refresh_list()

    def get_remaining_files(self) -> dict:
        """
        Returns:
            dict: the filtered file_loader dict, after removals/additions.
        """
        return dict(self.files)

    def open_file_preview(self, item: QListWidgetItem):
        """Preview the selected file: open PDFs externally, text files in a dialog."""
        key = item.data(Qt.ItemDataRole.UserRole)
        path = self.files.get(key)
        if not path or not os.path.exists(path):
            return

        if path.lower().endswith('.pdf'):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
            return

        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            content = "<Unable to preview this file>"

        dlg = QDialog(self)
        dlg.setWindowTitle(os.path.basename(path))
        v = QVBoxLayout(dlg)
        txt = QPlainTextEdit()
        txt.setReadOnly(True)
        txt.setPlainText(content)
        v.addWidget(txt)
        dlg.resize(600, 400)
        dlg.exec()

    def update_next_button(self):
        """Enable Next only if there's at least one file in the list."""
        self.next_btn.setEnabled(bool(self.files))

    def accept(self):
        """Override accept to block if no files remain."""
        if not self.files:
            return
        super().accept()

    @staticmethod
    def human_readable_size(size, decimal_places=2):
        """Convert a byte size into a human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.{decimal_places}f} {unit}"
            size /= 1024.0
        return f"{size:.{decimal_places}f} PB"
