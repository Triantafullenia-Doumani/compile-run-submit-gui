# Cimple Executor GUI  

Cimple Executor GUI is a lightweight Python application that provides a graphical interface for loading, compiling, executing, and remotely submitting code in the formats supported by your compiler—e.g., Cimple (`.ci`), intermediate (`.int`), and RISC‑V assembly (`.asm`). It has been tested with the Cimple compiler but will work with any compiler invokable via the standard command pattern described below.

---

## Features

- Load and manage source files via a user-friendly file dialog (tested with `.ci`, `.int`, `.asm`).  
- Compile and execute each stage (source → intermediate → assembly) with dedicated buttons.  
- Remotely submit output files to a lab server over SSH/SFTP with built-in progress dialogs.  

## Prerequisites

- **Python 3.7+** installed on your system.  
- A C/C++ compiler or any compatible compiler available in your `PATH`.  
- Install Python dependencies via `requirements.txt`.

> **Note:** Your compiler must be invokable as:
> ```bash
> python3 compiler.py <source_file> [extra args]
> ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Triantafullenia-Doumani/Submission-and-Management-System-for-Student-Assignments.git
   cd Submission-and-Management-System-for-Student-Assignments
   ```
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Launch the GUI:
```bash
python3 main.py
```

### Typical Workflow
1. **Load compiler script**: **File → Open**, select your compiler driver Python script (`.py`).  
2. **Load source file**: **File → Open**, pick any source file your compiler accepts (e.g., `.ci` or `.gr`).  
3. **Compile**: Click **Compile** to run the compiler, producing an intermediate file.  
4. **Load intermediate/assembly**: The GUI lists the generated intermediate and default assembly—browse to others if needed.  
5. **Run**: Execute the active stage and view its console output.  
6. **Submit**: Open **Remote Transfer**, verify credentials, select a host, and submit with progress feedback.

## File Structure & Descriptions
```
/your-project-root
│
├── src/
│   ├── gui/  
│   │   ├── buttons.py               # UI button definitions and signal connections
│   │   ├── buttons_handlers.py      # Core logic triggered by button clicks
│   │   ├── file_loader.py           # File-open dialogs and selected-file management
│   │   ├── host_list_worker.py      # QThread to fetch online lab hosts via SSH
│   │   ├── remote_transfer_dialog.py# Dialog for SSH credential entry and validation
│   │   ├── turnin_worker.py         # QThread to perform remote file submission
│   │   └── main_window.py           # Main application window assembly and layout
│   │
│   └── logic/  
│       ├── assembly_executer.py     # Executes RISC‑V `.asm` via an external tool
│       ├── compiler.py              # Wraps compiler invocation and captures output
│       ├── c_executer.py            # Runs compiled C binaries and retrieves results
│       ├── int_to_c_translator.py   # Converts `.int` intermediate code to C source
│       ├── runner.py                # Coordinates compilation, translation, and execution steps
│       └── submit_files.py          # SSH/SFTP functions for host lookup and `turnin` submission
│
├── main.py                         # Entry point: initializes QApplication and shows GUI
├── README.md                       # This document
└── requirements.txt                # Python package dependencies (PyQt6, Paramiko, etc.)
```

## Contributing

We welcome improvements, bug fixes, and new features:
1. Fork the repository.  
2. Create a feature branch: `git checkout -b feature-name`.  
3. Commit your changes: `git commit -m "Add awesome feature"`.  
4. Push and open a Pull Request on GitHub.  

Please follow the existing code style and include tests when applicable.

