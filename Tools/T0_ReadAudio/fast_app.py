import sys
import os
pckg_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(pckg_dir)

import logging
from ReadAudio import ReadAudio
from Tools.utils import ToolFastApp, load_yaml, log_config

if __name__ == '__main__':

    log_config()

    logging.info("Starting the T0_ReadAudio process...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")
    nao_ip = params["nao_ip"]
    params = params["T0_ReadAudio"]

    # Initialize the ReadAudio object
    read_audio = ReadAudio(
        nao_ip=nao_ip,
        input_wav_file=params["input_wav_file"]
    )
    logging.info("T0_ReadAudio object initialized successfully.")

    T0_fast_app = ToolFastApp(
        command_dict        = {"start": read_audio.start},
        get_status_function = read_audio.get_running,
        status_file         = "Tools/T0_ReadAudio/fast_com/status.txt",
        command_file        = "Tools/T0_ReadAudio/fast_com/command.txt"
    )

    logging.info("T0_ReadAudio process started successfully.")

    T0_fast_app.run()