import subprocess
import time
import os
from utils import load_yaml

server_processes = []

def get_ollama_app_path():
    # Get the path to the Ollama app executable
    # This path is specific to my Windows machine
    # let's consider that the path is \\AppData\\Local\\Programs\\Ollama\\ollama app.exe from the user's home directory

    # first get the user's home directory
    user_home = os.path.expanduser("~")
    # then append the rest of the path
    ollama_app_path = os.path.join(user_home, "AppData", "Local", "Programs", "Ollama", "ollama app.exe")

    return ollama_app_path

def start_servers():

    params = load_yaml("Tools/parameters.yaml")

    server_command_T = []

    for tool, tool_params in params.items():
        if tool == "nao_ip":
            continue
        command_str = f"py -{tool_params['python_version']} Tools/{tool}/fast_app.py"
        server_command_T.append(command_str)

    # Start the Ollama app in a separate subprocess
    subprocess.Popen(get_ollama_app_path(), shell=True)
    time.sleep(3)

    # Start each server in a separate subprocess
    for server_command in server_command_T:
        if server_command:
            server_processes.append(subprocess.Popen(server_command, shell=True))


def stop_servers():
    # Terminate each server process
    for process in server_processes:
        process.terminate()
    # Wait for all processes to terminate
    for process in server_processes:
        process.wait()

if __name__ == "__main__":

    import argparse
    from utils import copy_parameters

    # Instantiate the parser
    parser = argparse.ArgumentParser()
    # Add optional arguments
    parser.add_argument("--params", help="Path to the parameters file", default="StateMachine/SM_NAO_parameters.yaml")
    # Parse the arguments
    args = parser.parse_args()

    # copy the parameters file to the Tools folder
    copy_parameters(args.params, "Tools/parameters.yaml")

    try:
        start_servers()

        # Keep the script running until a keyboard interrupt occurs
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Stopping servers...")
        stop_servers()