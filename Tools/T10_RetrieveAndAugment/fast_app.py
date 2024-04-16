import sys
import os
pckg_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(pckg_dir)

import logging
from RetrieveAndAugment import RetrieveAndAugment
from Tools.utils import ToolFastApp, load_yaml

if __name__ == '__main__':

    # Set up the logging configuration
    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    logging.info("Starting the RetrieveAndAugment API server...")

    # Load the configuration parameters from the config file
    all_params = load_yaml("Tools/parameters.yaml")
    params = all_params["T10_RetrieveAndAugment"]
    ollama_model_name = all_params["T2_TextGeneration"]["model_name"]

    # Initialize the RetrieveAndAugment object
    RetrieveAndAugment = RetrieveAndAugment(
        input_database_folder    = params["input_database_folder"],
        input_question_text_file = params["input_text_file"],
        output_text_file         = params["output_text_file"],
        output_csv_file          = params["output_csv_file"],
        load_directory           = params["load_directory"],
        ollama_model             = ollama_model_name,
        input_additional_files   = params["input_additional_files"],
        number_of_results        = params["number_of_results"],
        chunk_size               = params["chunk_size"]
    )
    logging.info("RetrieveAndAugment object initialized successfully.")

    T10_fast_app = ToolFastApp(
        command_dict        = {"start": RetrieveAndAugment.start, "update": RetrieveAndAugment.update_vectordb},
        get_status_function = RetrieveAndAugment.get_running,
        status_file         = "Tools/T10_RetrieveAndAugment/fast_com/status.txt",
        command_file        = "Tools/T10_RetrieveAndAugment/fast_com/command.txt"
    )

    T10_fast_app.run()