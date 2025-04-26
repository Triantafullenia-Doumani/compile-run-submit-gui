import os
import subprocess
from PyQt6.QtWidgets import QFileDialog
from src.logic.compiler import compile_code
from src.logic.assembly_executor import AssemblyExecutor
from src.logic.c_executor import CExecutor
from src.logic.int_to_c_translator import write_to_c, extract_input_variables
from PyQt6.QtWidgets import QInputDialog

def run_compiler(compiler_path, source_path, output_box, extra_args=""):
    compile_code(compiler_path, source_path, output_box, extra_args)

def run_intermediate_code(source_path, output_box):
    if not source_path:
        output_box.append("No source file selected.")
        return
    base, _ = os.path.splitext(source_path)
    int_file = base + ".int"
    project_folder = os.getcwd()
    c_folder = os.path.join(project_folder, "c")
    os.makedirs(c_folder, exist_ok=True)
    c_file = os.path.join(c_folder, os.path.basename(base) + ".c")
    executable = os.path.join(project_folder, "generated.out")

    output_box.append("Converting intermediate code to C...")
    write_to_c(int_file, c_file, output_box)

    try:
        result = subprocess.run(["gcc", c_file, "-o", executable],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            output_box.append("Compilation error:")
            output_box.append(result.stderr)
            return
        output_box.append("Compilation successful.")
    except Exception as e:
        output_box.append(f"Compilation failed: {e}")
        return

    # Extract inputs and run
    inputs = extract_input_variables(int_file)
    executor = CExecutor(executable, output_box, input_names=inputs)
    executor.output_signal.connect(lambda txt: output_box.append(txt))
    executor.start()
    return executor


def run_assembly_code(asm_path, output_box):
    if not asm_path:
        output_box.append("No assembly file selected.")
        return None

    # count how many inputs the asm program needs
    def count_inputs(file_path):
        count = 0
        with open(file_path, 'r') as f:
            for line in f:
                if "call read_int" in line:
                    count += 1
        return count

    num_inputs = count_inputs(asm_path)
    inputs = []
    for i in range(num_inputs):
        txt, ok = QInputDialog.getText(None, "Assembly Input", f"Enter input #{i+1}:")
        if not ok:
            output_box.append("Input cancelled.")
            return None
        inputs.append(txt)

    executor = AssemblyExecutor(asm_path, output_box, inputs=inputs)
    executor.output_signal.connect(output_box.append)
    executor.start()
    return executor