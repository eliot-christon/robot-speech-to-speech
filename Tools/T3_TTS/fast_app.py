import sys
import os
pckg_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(pckg_dir)

import logging
from TextToSpeech import TextToSpeech
from Tools.utils import ToolFastApp, load_yaml

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