from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTextEdit,
    QLineEdit, QListWidget, QGroupBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from src.gui.buttons_handlers import (
    select_compiler_file, select_source_file, update_run_compile_state,
    run_compiler_action, select_intermediate_file, run_intermediate_action,
    select_assembly_file, run_assembly_wrapper, select_report_file,
    load_more_files, update_chosen_files_list, open_file_item,
    remote_turnin, auto_scroll
)

class ButtonsUI(QWidget):
    def __init__(self):
        super().__init__()
        font = QFont()
        font.setPointSize(11)
        self.setFont(font)

        self.file_loader = {}
        self.assembly_executor = None
        self.intermediate_executor = None

        # Output box
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.textChanged.connect(lambda: auto_scroll(self))

        # Main layout
        main_layout = QHBoxLayout(self)
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(30)

        # --- Compilation group ---
        compiler_box = QGroupBox("Compilation")
        compiler_box.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        c_layout = QVBoxLayout()
        c_layout.setContentsMargins(5, 5, 5, 5)
        c_layout.setSpacing(4)

        # Compiler picker
        comp_row = QHBoxLayout()
        comp_row.setSpacing(4)
        self.compiler_entry = QLineEdit(readOnly=True)
        self.compiler_entry.setMaximumWidth(220)
        self.compiler_entry.setPlaceholderText("Select compiler script...")
        comp_btn = QPushButton("Select Compiler")
        comp_btn.clicked.connect(lambda: select_compiler_file(self))
        comp_row.addWidget(self.compiler_entry)
        comp_row.addWidget(comp_btn)
        c_layout.addLayout(comp_row)

        # Source picker
        src_row = QHBoxLayout()
        src_row.setSpacing(4)
        self.source_entry = QLineEdit(readOnly=True)
        self.source_entry.setMaximumWidth(220)
        self.source_entry.setPlaceholderText("Select source file...")
        src_btn = QPushButton("Select Source")
        src_btn.clicked.connect(lambda: select_source_file(self))
        src_row.addWidget(self.source_entry)
        src_row.addWidget(src_btn)
        c_layout.addLayout(src_row)

        # Run compiler button
        self.run_compile_button = QPushButton("Run Compiler")
        self.run_compile_button.setEnabled(False)
        self.run_compile_button.clicked.connect(lambda: run_compiler_action(self))
        run_row = QHBoxLayout()
        run_row.addStretch()
        run_row.addWidget(self.run_compile_button)
        c_layout.addLayout(run_row)

        compiler_box.setLayout(c_layout)
        controls_layout.addWidget(compiler_box)

        # --- Intermediate Code group ---
        self.inter_box = QGroupBox("Intermediate Code")
        self.inter_box.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        i_layout = QHBoxLayout()
        i_layout.setContentsMargins(5, 5, 5, 5)
        i_layout.setSpacing(4)
        self.intermediate_file_entry = QLineEdit(readOnly=True)
        self.intermediate_file_entry.setMaximumWidth(220)
        int_btn = QPushButton("Browse .int")
        int_btn.clicked.connect(lambda: select_intermediate_file(self))
        self.run_intermediate_button = QPushButton("Run")
        self.run_intermediate_button.clicked.connect(lambda: run_intermediate_action(self))
        i_layout.addWidget(self.intermediate_file_entry)
        i_layout.addWidget(int_btn)
        i_layout.addWidget(self.run_intermediate_button)
        self.inter_box.setLayout(i_layout)
        self.inter_box.setVisible(False)
        controls_layout.addWidget(self.inter_box)

        # --- Assembly Code group ---
        self.asm_box = QGroupBox("Assembly Code")
        self.asm_box.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        a_layout = QHBoxLayout()
        a_layout.setContentsMargins(5, 5, 5, 5)
        a_layout.setSpacing(4)
        self.assembly_file_entry = QLineEdit(readOnly=True)
        self.assembly_file_entry.setMaximumWidth(220)
        asm_btn = QPushButton("Browse .asm")
        asm_btn.clicked.connect(lambda: select_assembly_file(self))
        self.run_asm_button = QPushButton("Run")
        self.run_asm_button.clicked.connect(lambda: run_assembly_wrapper(self))
        a_layout.addWidget(self.assembly_file_entry)
        a_layout.addWidget(asm_btn)
        a_layout.addWidget(self.run_asm_button)
        self.asm_box.setLayout(a_layout)
        self.asm_box.setVisible(False)
        controls_layout.addWidget(self.asm_box)

        # --- Report File group ---
        report_box = QGroupBox("Report File")
        report_box.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        r_layout = QHBoxLayout()
        r_layout.setContentsMargins(5, 5, 5, 5)
        r_layout.setSpacing(4)
        self.report_file_entry = QLineEdit(readOnly=True)
        self.report_file_entry.setMaximumWidth(220)
        rpt_btn = QPushButton("Select Report")
        rpt_btn.clicked.connect(lambda: select_report_file(self))
        r_layout.addWidget(self.report_file_entry)
        r_layout.addWidget(rpt_btn)
        report_box.setLayout(r_layout)
        controls_layout.addWidget(report_box)

        # Load more files
        more_btn = QPushButton("Load More Files")
        more_btn.clicked.connect(lambda: load_more_files(self))
        controls_layout.addWidget(more_btn)

        # Chosen files list
        self.chosen_files_list = QListWidget()
        self.chosen_files_list.setFixedHeight(90)
        self.chosen_files_list.itemDoubleClicked.connect(lambda item: open_file_item(self, item))
        controls_layout.addWidget(self.chosen_files_list)

        # Submit button
        turnin_row = QHBoxLayout()
        turnin_row.addStretch()
        turnin_btn = QPushButton("Turnin")
        turnin_btn.clicked.connect(lambda: remote_turnin(self))
        turnin_row.addWidget(turnin_btn)
        turnin_row.addStretch()
        controls_layout.addLayout(turnin_row)

        main_layout.addLayout(controls_layout, 1)
        main_layout.addWidget(self.output_box, 2)

        self.setLayout(main_layout)
        self.adjustSize()

        update_run_compile_state(self)
        update_chosen_files_list(self)