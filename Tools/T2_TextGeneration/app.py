import sys
import os
pckg_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(pckg_dir)

import logging
from .TextGeneration import TextGeneration
from ..utils import ToolFastApp, load_yaml
from ..ToolApiApp import ToolApiApp

if __name__ == '__main__':

    # Set up the logging configuration
    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

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

    T2_app = ToolApiApp(
        command_dict        = {"start": text_generation.start,
                               "status": text_generation.get_running},
        name="T2_TextGeneration",
        port=5002
    )

    T2_app.run()