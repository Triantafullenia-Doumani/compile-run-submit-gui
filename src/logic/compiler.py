import subprocess
import shlex

def compile_code(compiler_file, source_file, output_box,run_asm_button, extra_args=""):
    """
    Executes the compiler script on the source file and displays output.
    """
    try:
        # Build the command
        command = ["python", compiler_file, source_file]
        if extra_args:
            command += shlex.split(extra_args)

        # Run the compiler
        result = subprocess.run(command, capture_output=True, text=True)

        # Show output or errors
        output = result.stdout if result.stdout else result.stderr
        output_box.setPlainText(output)
    except Exception as e:
        output_box.setPlainText(f"Error: {e}")

