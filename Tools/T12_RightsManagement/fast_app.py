import sys
import os
pckg_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(pckg_dir)

import logging
from .RightsManagement import RightsManagement
from ..utils import ToolFastApp, load_yaml, log_config

if __name__ == '__main__':

    log_config()

    logging.info("Starting the T12_RightsManagement process...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")["T12_RightsManagement"]

    # Initialize the Leds object
    rights_management = RightsManagement(
        input_url_api_request           = params["input_url_api_request"],
        input_person_reconized_file     = params["input_person_reconized_file"],
        input_people_folder             = params["input_people_folder"],
        output_documents_autorized_file = params["output_documents_autorized_file"],
        output_actions_autorized_file   = params["output_actions_autorized_file"]
    )
    logging.info("T12_RightsManagement object initialized successfully.")

    T12_fast_app = ToolFastApp(
        command_dict        = {"start": rights_management.start},
        get_status_function = rights_management.get_running,
        status_file         = "Tools/T12_RightsManagement/fast_com/status.txt",
        command_file        = "Tools/T12_RightsManagement/fast_com/command.txt"
    )

    T12_fast_app.run()