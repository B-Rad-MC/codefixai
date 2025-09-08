import os

def get_file_content(working_directory, file_path):
    try:
        full_path = os.path.join(working_directory, file_path)
        if not os.path.abspath(full_path).startswith(os.path.abspath(working_directory)):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(full_path):
            return f'Error: File not found or is not a regular file: "{full_path}"'
        with open(full_path) as file:
            file_string = file.read()
            if len(file_string) > 10000:
                file_string = file_string[:10000] + f'[...File "{full_path}" truncated at 10000 characters]'
            return file_string
    except Exception as e:
        return f"Error: {e}"