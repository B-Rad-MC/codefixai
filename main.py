import os, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.run_python_file import run_python_file
from functions.write_file import write_file

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads and returns the contents of the specified file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to be read, relative to the working directory.",
            ),
        },
    ),
)
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes the specified Python file with optional arguments, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to be executed, relative to the working directory.",
            ), "args": types.Schema(
                type=types.Type.ARRAY,
                description="An optional list of string arguments. If not provided, the file will execute without arguments",
                items= types.Schema(type=types.Type.STRING)
            )
        },
    ),
)
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites new content to the specified file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to be written to, relative to the working directory.",
            ), "content": types.Schema(
                type=types.Type.STRING,
                description="The new content to write to the file.",
            )
        },
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file
    ]
)

def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    callable_functions = {"get_file_content" : get_file_content, "get_files_info" : get_files_info, "run_python_file" : run_python_file, "write_file" : write_file}
    if function_call_part.name in callable_functions:
        args = dict(function_call_part.args)
        args["working_directory"] = "./calculator"
        result = callable_functions[function_call_part.name](**args)
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"result": result},
                )
            ],
        )
    else:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
                )
            ],
        )

def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """
    if len(sys.argv) >= 2:
        prompt = sys.argv[1]
    else:
        print("No prompt provided")
        exit(1)
    messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]
    for i in range(20):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-001", 
                contents=messages, 
                config=types.GenerateContentConfig(system_instruction=system_prompt, tools=[available_functions])
                )
            for candidate in response.candidates:
                messages.append(candidate.content)
            if response.function_calls:
                for part in response.function_calls:
                    called_response = call_function(part).parts[0].function_response.response
                    if called_response is not None and len(called_response["result"]) > 0:
                        messages.append(types.Content(role="user", parts=[types.Part(text=str(called_response["result"]))]))
                        if "--verbose" in sys.argv:
                            print(f"-> {called_response["result"]}")
                    else:
                        raise Exception("Error: No function response found")

            elif response.text:
                print(response.text)
                break
            else:
                print("No text or function calls returned.")
                break
            if "--verbose" in sys.argv:
                print(f"User prompt: {prompt}")
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
