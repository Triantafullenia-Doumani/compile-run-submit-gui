import os
from PyQt6.QtWidgets import (
    QFileDialog, QListWidgetItem, QDialog, QPlainTextEdit, QInputDialog,
    QMessageBox, QVBoxLayout, QProgressDialog
)
from PyQt6.QtGui import QTextCursor, QDesktopServices
from PyQt6.QtCore import Qt, QUrl

from src.logic.runner import (
    run_compiler, run_intermediate_code, run_assembly_code
)
from src.gui.file_loader import FileLoader
from src.gui.confirm_submission_dialog import ConfirmSubmissionDialog
from src.gui.remote_transfer_dialog import RemoteTransferDialog
from src.gui.host_list_worker import HostListWorker
from src.gui.turnin_worker import TurninWorker
from src.logic.submit_files import get_online_lab_hosts, execute_remote_turnin

def select_compiler_file(ui):
    path, _ = QFileDialog.getOpenFileName(
        ui,
        "Select Compiler Python File",
        "",
        "Python Files (*.py)"
    )
    if path:
        ui.file_loader['compiler'] = path
        ui.compiler_entry.setText(os.path.basename(path))
        update_run_compile_state(ui)
        update_chosen_files_list(ui)


def select_source_file(ui):
    path, _ = QFileDialog.getOpenFileName(
        ui,
        "Select Source File",
        "",
        "Source Files (*)"
    )
    if path:
        ui.file_loader['source'] = path
        ui.source_entry.setText(os.path.basename(path))
        update_run_compile_state(ui)
        update_chosen_files_list(ui)


def update_run_compile_state(ui):
    ui.run_compile_button.setEnabled(
        bool(ui.file_loader.get('compiler')) and bool(ui.file_loader.get('source'))
    )


def run_compiler_action(ui):
    run_compiler(
        ui.file_loader.get('compiler', ''),
        ui.file_loader.get('source', ''),
        ui.output_box
    )
    try:
        defaults = FileLoader.load_default_files(
            ui.file_loader.get('source', '')
        )
    except Exception as e:
        ui.output_box.append(f"Error: {e}")
        return
    if defaults.get('int'):
        ui.file_loader['intermediate'] = defaults['int']
        ui.intermediate_file_entry.setText(
            os.path.basename(defaults['int'])
        )
        ui.inter_box.setVisible(True)
    if defaults.get('asm'):
        ui.file_loader['assembly'] = defaults['asm']
        ui.assembly_file_entry.setText(
            os.path.basename(defaults['asm'])
        )
        ui.asm_box.setVisible(True)
    update_chosen_files_list(ui)


def select_intermediate_file(ui):
    path, _ = QFileDialog.getOpenFileName(
        ui,
        "Select Intermediate File",
        "",
        "Intermediate Files (*.int)"
    )
    if path:
        ui.file_loader['intermediate'] = path
        ui.intermediate_file_entry.setText(os.path.basename(path))
        update_chosen_files_list(ui)


def run_intermediate_action(ui):
    ui.intermediate_executor = run_intermediate_code(
        ui.file_loader.get('intermediate', ''),
        ui.output_box
    )


def select_assembly_file(ui):
    path, _ = QFileDialog.getOpenFileName(
        ui,
        "Select Assembly File",
        "",
        "Assembly Files (*.asm *.s)"
    )
    if path:
        ui.file_loader['assembly'] = path
        ui.assembly_file_entry.setText(os.path.basename(path))
        update_chosen_files_list(ui)


def run_assembly_wrapper(ui):
    ui.assembly_executor = run_assembly_code(
        ui.file_loader.get('assembly', ''),
        ui.output_box
    )


def select_report_file(ui):
    path, _ = QFileDialog.getOpenFileName(
        ui,
        "Select Report File",
        "",
        "PDF Files (*.pdf)"
    )
    if path:
        ui.file_loader['report'] = path
        ui.report_file_entry.setText(os.path.basename(path))
        update_chosen_files_list(ui)


def load_more_files(ui):
    paths, _ = QFileDialog.getOpenFileNames(
        ui,
        "Load More Files",
        "",
        "All Files (*)"
    )
    for p in paths:
        ui.file_loader[p] = p
    update_chosen_files_list(ui)


def update_chosen_files_list(ui):
    ui.chosen_files_list.clear()
    for key, path in ui.file_loader.items():
        item = QListWidgetItem(os.path.basename(path))
        item.setData(Qt.ItemDataRole.UserRole, path)
        ui.chosen_files_list.addItem(item)


def open_file_item(ui, item):
    path = item.data(Qt.ItemDataRole.UserRole)
    if not os.path.exists(path):
        ui.output_box.append(f"File not found: {path}")
        return
    if path.lower().endswith('.pdf'):
        QDesktopServices.openUrl(
            QUrl.fromLocalFile(path)
        )
    else:
        dlg = QDialog(ui)
        dlg.setWindowTitle(os.path.basename(path))
        txt = QPlainTextEdit()
        txt.setReadOnly(True)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                txt.setPlainText(f.read())
        except Exception as e:
            txt.setPlainText(f"Error loading file:\n{e}")
        layout = QVBoxLayout()
        layout.addWidget(txt)
        dlg.setLayout(layout)
        dlg.resize(600, 400)
        dlg.exec()


        
def remote_turnin(ui):
    # keep a snapshot so we can restore on cancel
    original_files = dict(ui.file_loader)

    # 1. Confirm the files
    confirm = ConfirmSubmissionDialog(ui.file_loader, ui)
    if confirm.exec() != QDialog.DialogCode.Accepted:
        # restore in case dialog mutated the list
        ui.file_loader = original_files
        update_chosen_files_list(ui)
        ui.output_box.append("Submission canceled.")
        return

    ui.file_loader = confirm.get_remaining_files()
    update_chosen_files_list(ui)

    # 2. Login
    login_dlg = RemoteTransferDialog(ui)
    if login_dlg.exec() != QDialog.DialogCode.Accepted:
        # also restore if user cancels before login
        ui.file_loader = original_files
        update_chosen_files_list(ui)
        ui.output_box.append("Login canceled.")
        return

    creds = login_dlg.get_credentials()
    if not creds:
        ui.file_loader = original_files
        update_chosen_files_list(ui)
        ui.output_box.append("No credentials provided.")
        return
    user, pw = creds

    # 3. Lookup hosts in background
    ui.host_thread = HostListWorker(user, pw)
    ui.host_progress = QProgressDialog("Retrieving online hosts...", None, 0, 0, ui)
    ui.host_progress.setWindowModality(Qt.WindowModality.WindowModal)
    ui.host_progress.setCancelButton(None)
    ui.host_progress.show()

    def on_hosts(hosts: list[str]):
        ui.host_progress.close()
        ui.host_thread = None
        if not hosts:
            ui.output_box.append("No lab workstations online.")
            # restore original files so next submit starts clean
            ui.file_loader = original_files
            update_chosen_files_list(ui)
            return

        host, ok = QInputDialog.getItem(ui, "Select Lab Workstation", "Online:", hosts, 0, False)
        if not ok or not host:
            ui.output_box.append("No workstation selected.")
            ui.file_loader = original_files
            update_chosen_files_list(ui)
            return

        ac, ok = QInputDialog.getText(ui, "Assignment@Course", "Enter assignment@course:")
        if not ok or "@" not in ac:
            ui.output_box.append("Invalid format.")
            ui.file_loader = original_files
            update_chosen_files_list(ui)
            return
        assign, course = ac.split("@", 1)

        # 4. Submit in background
        ui.turnin_thread = TurninWorker(user, pw, ui.file_loader, assign.strip(), course.strip(), host)
        ui.turnin_progress = QProgressDialog("Submitting files...", None, 0, 0, ui)
        ui.turnin_progress.setWindowModality(Qt.WindowModality.WindowModal)
        ui.turnin_progress.setCancelButton(None)
        ui.turnin_progress.show()

        def on_turnin_done(out: str, err: str):
            ui.turnin_progress.close()
            ui.output_box.append(err or out)
            ui.turnin_thread = None
            # clear file list after successful submit
            if not err:
                ui.file_loader.clear()
                update_chosen_files_list(ui)

        ui.turnin_thread.finished.connect(on_turnin_done)
        ui.turnin_thread.start()

    def on_hosts_error(message: str):
        ui.host_progress.close()
        ui.output_box.append(message)
        ui.host_thread = None
        ui.file_loader = original_files
        update_chosen_files_list(ui)

    ui.host_thread.hosts_ready.connect(on_hosts)
    ui.host_thread.error.connect(on_hosts_error)
    ui.host_thread.start()

def auto_scroll(ui):
    cursor = ui.output_box.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    ui.output_box.setTextCursor(cursor)
    ui.output_box.ensureCursorVisible()
