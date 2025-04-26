from PyQt6.QtWidgets import QWidget, QPushButton, QLineEdit, QFileDialog, QGridLayout
import os

class FileLoader(QWidget):
    def __init__(self):
        super().__init__()
        self.loaded_files = {"compiler": None, "source": None}
        
        self.layout = QGridLayout()
        
        # Compiler selector
        self.load_compiler_button = QPushButton("Select Compiler (.py)")
        self.load_compiler_button.clicked.connect(lambda: self.load_file("compiler"))
        self.layout.addWidget(self.load_compiler_button, 0, 0)
        
        self.compiler_entry = QLineEdit()
        self.compiler_entry.setReadOnly(True)
        self.layout.addWidget(self.compiler_entry, 0, 1)
        
        # Source selector (any extension)
        self.load_source_button = QPushButton("Select Source File")
        self.load_source_button.clicked.connect(lambda: self.load_file("source"))
        self.layout.addWidget(self.load_source_button, 0, 2)
        
        self.source_entry = QLineEdit()
        self.source_entry.setReadOnly(True)
        self.layout.addWidget(self.source_entry, 0, 3)
        
        self.setLayout(self.layout)
    
    def load_file(self, file_type):
        file_types = {"compiler": "Python Files (*.py)", "source": "All Files (*)"}
        caption = "Select Compiler (.py)" if file_type == "compiler" else "Select Source File"
        file_path, _ = QFileDialog.getOpenFileName(self, caption, "", file_types[file_type])
        
        if file_path:
            self.loaded_files[file_type] = file_path
            if file_type == "compiler":
                self.compiler_entry.setText(os.path.basename(file_path))
            else:
                self.source_entry.setText(os.path.basename(file_path))

    @staticmethod
    def load_default_files(source_filepath):
        """
        Given any source file path, look for its .int and .asm in default subfolders:
        - int/<basename>.int
        - asm/<basename>.asm
        """
        if not source_filepath:
            return {}
        base = os.path.splitext(os.path.basename(source_filepath))[0]
        int_fp = os.path.join("int", f"{base}.int")
        asm_fp = os.path.join("asm", f"{base}.asm")

        inter, asm = None, None
        if os.path.exists(int_fp):
            try:
                with open(int_fp, "r") as f:
                    inter = f.read()
            except Exception:
                inter = None
        if os.path.exists(asm_fp):
            try:
                with open(asm_fp, "r") as f:
                    asm = f.read()
            except Exception:
                asm = None

        result = {"source": source_filepath}
        if inter:
            result.update({"int": int_fp, "intermediate_content": inter})
        if asm:
            result.update({"asm": asm_fp, "assembly_content": asm})

        return result
