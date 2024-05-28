import sys
import os
pckg_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(pckg_dir)

import logging
from Gesture import Gesture
from Tools.utils import ToolFastApp, load_yaml, log_config

if __name__ == '__main__':

    log_config()

    logging.info("Starting the T11_Gesture process...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")
    nao_ip = params["nao_ip"]
    params = params["T11_Gesture"]

    # Initialize the Leds object
    gesture = Gesture(
        nao_ip = nao_ip,
    )
    logging.info("T11_Gesture object initialized successfully.")

    T11_fast_app = ToolFastApp(
        command_dict        = {"start": gesture.start, "stop": gesture.stop, "hi": gesture.say_hi, "bye": gesture.say_bye, "sit": gesture.sit},
        get_status_function = gesture.get_running,
        status_file         = "Tools/T11_Gesture/fast_com/status.txt",
        command_file        = "Tools/T11_Gesture/fast_com/command.txt"
    )

    T11_fast_app.run()