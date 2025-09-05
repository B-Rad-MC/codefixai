import os

def get_files_info(working_directory, directory="."):
    try:
        full_path = os.path.join(working_directory, directory)
        if not os.path.abspath(full_path).startswith(os.path.abspath(working_directory)):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not os.path.isdir(full_path):
            return f'Error: "{full_path}" is not a directory'
        return_string = ""
        for file in os.listdir(full_path):
            file_name = os.path.join(full_path, file)
            file_string = f" - {file}: file_size={os.path.getsize(file_name)} bytes, is_dir={os.path.isdir(file_name)}"
            if len(return_string) == 0:
                return_string = file_string
            else:
                return_string += " \n" + file_string
        return return_string
    except Exception as e:
        return f"Error: {e}"