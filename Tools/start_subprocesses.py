import subprocess
import time
import os
from .utils import load_yaml


"""
This script starts the Ollama app and all the tools in separate subprocesses.
The Ollama app is started first, then each tool is started from its own virtual environment.
"""


processes = []

def get_ollama_app_path():
    # Get the path to the Ollama app executable
    # This path is specific to my Windows machine
    # let's consider that the path is \\AppData\\Local\\Programs\\Ollama\\ollama app.exe from the user's home directory

    # first get the user's home directory
    user_home = os.path.expanduser("~")
    # then append the rest of the path
    # TODO: find a way to run ollama app on linux or on other path installations
    ollama_app_path = os.path.join(user_home, "AppData", "Local", "Programs", "Ollama", "ollama app.exe")

    return ollama_app_path

def start_processes():
    """Start the Ollama app and all the tools in separate subprocesses."""

    params = load_yaml("Tools/parameters.yaml")

    if os.name == "posix":
        linux = True
    else:
        linux = False

    process_command_T = []

    for tool, tool_params in params.items():
        if tool == "nao_ip" or tool == "envs_folder":
            continue

        if tool_params["python_version"] == "2.7":
            venv_tool = "nao_env"
        else:
            venv_tool = tool

        if linux:
            activate_path = f"Tools/{venv_tool}/venv/bin/activate"
        else: # Windows
            activate_path = f"Tools\\{venv_tool}\\venv\\Scripts\\activate"

        if os.path.exists(activate_path):
            print(f"Launching {tool} from its venv...")
            if linux:
                command_str = f". {activate_path} && python -m Tools.{tool}.fast_app" 
            else: # Windows
                command_str = f"{activate_path}.bat && python -m Tools.{tool}.fast_app"         
        else:
            raise FileNotFoundError(f"Could not find the virtual environment for {tool}, {activate_path}")
        process_command_T.append(command_str)

    # Start the Ollama app in a separate subprocess
    subprocess.Popen(get_ollama_app_path(), shell=True)
    time.sleep(3)

    # Start each process in a separate subprocess
    for command in process_command_T:
        if command:
            processes.append(subprocess.Popen(command, shell=True))


def stop_processes():
    # Terminate each process
    for process in processes:
        process.terminate()
    # Wait for all processes to terminate
    for process in processes:
        process.wait()

if __name__ == "__main__":

    import argparse
    from .utils import copy_parameters, log_config

    # clear Tools/log.txt
    with open("Tools/log.txt", "w") as file:
        file.write("")

    log_config()

    # Instantiate the parser
    parser = argparse.ArgumentParser()
    # Add optional arguments
    parser.add_argument("--params", help="Path to the parameters file", default="StateMachine/SM_NAO_parameters.yaml")
    # Parse the arguments
    args = parser.parse_args()

    # copy the parameters file to the Tools folder
    copy_parameters(args.params, "Tools/parameters.yaml", "Tools/nao_ip.txt")

    try:
        start_processes()

        # Keep the script running until a keyboard interrupt occurs
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Stopping processes...")
        stop_processes()
    