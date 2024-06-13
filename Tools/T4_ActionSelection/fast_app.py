import sys
import os
pckg_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(pckg_dir)

import logging
from .ActionSelection import ActionSelection
from ..utils import ToolFastApp, load_yaml, log_config


if __name__ == '__main__':
    import logging

    log_config()

    logging.info("Starting the T4_ActionSelection process...")

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
    logging.info("T4_ActionSelection object initialized successfully.")

    T4_fast_app = ToolFastApp(
        command_dict        = {"start": action_selection.start, "train": action_selection.train_classifier},
        get_status_function = action_selection.get_running,
        status_file         = "Tools/T4_ActionSelection/fast_com/status.txt",
        command_file        = "Tools/T4_ActionSelection/fast_com/command.txt"
    )

    T4_fast_app.run()