import sys
import os
pckg_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(pckg_dir)

import logging
from ActionSelection import ActionSelection
from Tools.utils import ToolFastApp, load_yaml


if __name__ == '__main__':
    import logging

    # Set up the logging configuration
    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    logging.info("Starting the Action Selection API server...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")
    model_name = params["T2_TextGeneration"]["model_name"]
    params = params["T4_ActionSelection"]

    # Initialize the ActionSelection object
    action_selection = ActionSelection(
        action_selection_dataset_path   = params["action_selection_dataset_path"],
        input_text_file                 = params["input_text_file"],
        output_text_file                = params["output_text_file"],
        pretrained_model_folder         = params["pretrained_model_folder"],
        model_name                      = model_name,
    )
    logging.info("Action Selection object initialized successfully.")

    T4_fast_app = ToolFastApp(
        command_dict        = {"start": action_selection.start},
        get_status_function = action_selection.get_running,
        status_file         = "Tools/T4_ActionSelection/fast_com/status.txt",
        command_file        = "Tools/T4_ActionSelection/fast_com/command.txt"
    )

    T4_fast_app.run()