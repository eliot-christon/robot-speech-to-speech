import sys
import os
pckg_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(pckg_dir)

import logging
from Leds import Leds
from Tools.utils import ToolFastApp, load_yaml

if __name__ == '__main__':

    # Set up the logging configuration
    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    logging.info("Starting the Leds API server...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")
    nao_ip = params["nao_ip"]
    params = params["T9_LEDS"]

    # Initialize the Leds object
    leds = Leds(
        nao_ip=nao_ip,
        input_text_file=params["input_text_file"]
    )
    logging.info("Leds object initialized successfully.")

    T9_fast_app = ToolFastApp(
        command_dict        = {"start": leds.start, "reset": leds.reset, "stop": leds.reset},
        get_status_function = leds.get_running,
        status_file         = "Tools/T9_LEDS/fast_com/status.txt",
        command_file        = "Tools/T9_LEDS/fast_com/command.txt"
    )

    T9_fast_app.run()