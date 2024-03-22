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
from TextToSpeech import TextToSpeech

if __name__ == '__main__':

    # Set up the logging configuration
    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    logging.info("Starting the Text-to-Speech API server...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")["T3_TTS"]

    # Initialize the TextToSpeech object
    text_to_speech = TextToSpeech(
        model_name = params["model_name"],
        input_text_file = params["input_text_file"],
        output_wav_file = params["output_wav_file"],
        speaker_wav_file = params["speaker_wav_file"],
        language = params["language"]
    )
    logging.info("Text-to-Speech object initialized successfully.")

    T3_fast_app = ToolFastApp(
        command_dict        = {"start": text_to_speech.start},
        get_status_function = text_to_speech.get_running,
        status_file         = "Tools/T3_TTS/fast_com/status.txt",
        command_file        = "Tools/T3_TTS/fast_com/command.txt"
    )

    T3_fast_app.run()