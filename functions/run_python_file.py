import os, subprocess

def run_python_file(working_directory, file_path, args=[]):
    try:
        full_path = os.path.join(working_directory, file_path)
        if not os.path.abspath(full_path).startswith(os.path.abspath(working_directory)):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.exists(full_path):
            return f'Error: File "{file_path}" not found.'
        if file_path[-3:] != ".py":
            return f'Error: "{file_path}" is not a Python file.'
        try:
            process = subprocess.run(["python", file_path] + args, timeout=30, capture_output=True, cwd=working_directory, text=True)
            if len(process.stdout) != 0:
                results = f"STDOUT: {process.stdout}, STDERR: {process.stderr}"
                if process.returncode != 0:
                    results += f", Process exited with code {process.returncode}"
            else:
                results = "No output produced"
            return results
        except Exception as e:
            return f"Error: executing Python file: {e}"
    except Exception as e:
        return f"Error: {e}"