import logging
import time
import yaml
import threading

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as exc:
            logging.error(exc)

def copy_parameters(from_yaml, to_yaml, nao_ip_file, envs_folder_file):
    data = load_yaml(from_yaml)
    with open(nao_ip_file, 'r') as file:
        nao_ip = file.read()
    with open(envs_folder_file, 'r') as file:
        envs_folder = file.read()
    data["nao_ip"] = nao_ip
    data["envs_folder"] = envs_folder
    with open(to_yaml, 'w') as file:
        yaml.dump(data, file)

class ToolFastApp:

    def __init__(self, command_dict, get_status_function, status_file, command_file):
        self.__command_dict = command_dict
        self.__get_status = get_status_function
        self.__status_file = status_file
        self.__command_file = command_file
        self.__lock = threading.Lock()  # Add a lock for thread safety

    def __erase_command(self):
        """Erase the command from the command file (text file)"""
        # check if the command is still the same
        with open(self.__command_file, 'w') as file:
            file.write("_")

    def __read_command(self):
        """Read the command from the command file (text file)"""
        with open(self.__command_file, 'r') as file:
            return file.read()

    def __write_status(self):
        """Write the status to the status file (text file)"""
        with open(self.__status_file, 'w') as file:
            file.write(str(self.__get_status()))

    def __execute_command(self, command):
        """Execute the command in a separate thread"""
        if command in self.__command_dict:
            logging.info("Executing command: " + command + " (" + self.__command_file + ")")
            threading.Thread(target=self.__command_dict[command]).start()

    def run(self):
        while True:
            try:
                with self.__lock:  # Acquire lock before reading and erasing command
                    command = self.__read_command()
                    if command != '_':  # Check if command is not empty
                        self.__execute_command(command)
                        time.sleep(0.01)
                        # check if the command is still the same
                        if command == self.__read_command():
                            self.__erase_command()
                self.__write_status()
                time.sleep(0.1)
            except KeyboardInterrupt:
                logging.info("Exiting the FastApp...")
                break

def log_config():
    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s', filename='Tools/log.txt', filemode='a')
    logging.getLogger().setLevel(logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('[%(levelname)s] - %(asctime)s - %(message)s'))
    logging.getLogger().addHandler(console)