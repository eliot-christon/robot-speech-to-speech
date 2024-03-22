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

class ToolFastApp:

    def __init__(self, command_dict, get_status_function, status_file, command_file):
        self.__command_dict = command_dict
        self.__get_status = get_status_function
        self.__status_file = status_file
        self.__command_file = command_file
        self.__lock = threading.Lock()  # Add a lock for thread safety

    def __erase_command(self):
        """Erase the command from the command file (text file)"""
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
        logging.info("Executing command: " + command)
        if command in self.__command_dict:
            threading.Thread(target=self.__command_dict[command]).start()

    def run(self):
        while True:
            with self.__lock:  # Acquire lock before reading and erasing command
                command = self.__read_command()
                if command != '_':  # Check if command is not empty
                    self.__execute_command(command)
                    self.__erase_command()
            self.__write_status()
            time.sleep(0.1)

#%% ================================================================================================

import logging
from SoundReceiverModule import SoundReceiverModule

if __name__ == '__main__':
    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    logging.info("Starting the RecordAudio API server...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")["T6_RecordAudio"]

    # Create a proxy to the NAO robot
    import naoqi
    myBroker = naoqi.ALBroker("myBroker",
                               "0.0.0.0",           # listen to anyone
                               0,                   # find a free port and use it
                               params["nao_ip"],    # parent broker IP
                               9559)                # parent broker port

    # Initialize the SoundReceiver object
    SoundReceiver = SoundReceiverModule(
        strModuleName="SoundReceiver",
        nao_ip=params["nao_ip"],
        output_wav_file=params["output_wav_file"],
        output_speech_detected_file=params["output_speech_detected_file"],
        channel=params["channel"],
        seconds_to_keep=params["seconds_to_keep"],
        sample_rate=params["sample_rate"],
        loudness_threshold=params["loudness_threshold"]
    )
    logging.info("RecordAudio object initialized successfully.")

    T6_fast_app = ToolFastApp(
        command_dict        = {"start": SoundReceiver.start, "stop": SoundReceiver.stop},
        get_status_function = SoundReceiver.get_running,
        status_file         = "Tools/T6_RecordAudio/fast_com/status.txt",
        command_file        = "Tools/T6_RecordAudio/fast_com/command.txt"
    )

    T6_fast_app.run()