import sys
import os
pckg_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(pckg_dir)

import logging
from TextGeneration import TextGeneration
from Tools.utils import ToolFastApp, load_yaml, log_config

if __name__ == '__main__':

    log_config()

    logging.info("Starting the Text Generation API server...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")["T2_TextGeneration"]

    # Initialize the SpeechToText object
    text_generation = TextGeneration(
        model_name              = params["model_name"],
        input_text_file         = params["input_text_file"],
        output_text_file        = params["output_text_file"],
        ollama_generate_options = params["ollama_generate_options"]
    )
    logging.info("Text Generation object initialized successfully.")

    T2_fast_app = ToolFastApp(
        command_dict        = {"start": text_generation.start},
        get_status_function = text_generation.get_running,
        status_file         = "Tools/T2_TextGeneration/fast_com/status.txt",
        command_file        = "Tools/T2_TextGeneration/fast_com/command.txt"
    )

    T2_fast_app.run()