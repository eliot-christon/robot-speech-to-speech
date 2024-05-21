import sys
import os
pckg_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(pckg_dir)

import logging
from SpeechToText import SpeechToText
from Tools.utils import ToolFastApp, load_yaml


if __name__ == '__main__':

    logging.info("Starting the Speech-to-Text API server...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")["T8_STT"]

    # Initialize the SpeechToText object
    speech_to_text = SpeechToText(
        model_size=params["model_size"],
        input_wav_file=params["input_wav_file"],
        output_text_file=params["output_text_file"]
    )
    logging.info("Speech-to-Text object initialized successfully.")

    T8_fast_app = ToolFastApp(
        command_dict        = {"start": speech_to_text.start, "stop": speech_to_text.stop},
        get_status_function = speech_to_text.get_running,
        status_file         = "Tools/T8_STT/fast_com/status.txt",
        command_file        = "Tools/T8_STT/fast_com/command.txt"
    )

    T8_fast_app.run()