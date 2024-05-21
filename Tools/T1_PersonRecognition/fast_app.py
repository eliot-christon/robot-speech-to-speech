import sys
import os
pckg_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(pckg_dir)

import logging
from PersonRecognition import PersonRecognition
from Tools.utils import ToolFastApp, load_yaml, log_config

if __name__ == '__main__':

    log_config()

    logging.info("Starting the PersonRecognition API server...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")["T1_PersonRecognition"]

    # Initialize the PersonRecognition object
    person_recognition = PersonRecognition(
        output_text_file    = params["output_text_file"],
        input_audio_file    = params["input_audio_file"],
        input_people_folder = params["input_people_folder"],
        input_model_dir     = params["input_model_dir"]
    )
    logging.info("PersonRecognition object initialized successfully.")

    T1_fast_app = ToolFastApp(
        command_dict        = {"start": person_recognition.start, "stop": person_recognition.stop},
        get_status_function = person_recognition.get_running,
        status_file         = "Tools/T1_PersonRecognition/fast_com/status.txt",
        command_file        = "Tools/T1_PersonRecognition/fast_com/command.txt"
    )

    T1_fast_app.run()