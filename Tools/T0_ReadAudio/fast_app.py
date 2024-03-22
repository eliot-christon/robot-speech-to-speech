import sys
import os
pckg_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(pckg_dir)

import logging
from ReadAudio import ReadAudio
from Tools.utils import ToolFastApp, load_yaml

if __name__ == '__main__':
    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    logging.info("Starting the ReadAudio process...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")["T0_ReadAudio"]

    # Initialize the ReadAudio object
    read_audio = ReadAudio(
        nao_ip=params["nao_ip"],
        input_wav_file=params["input_wav_file"]
    )
    logging.info("ReadAudio object initialized successfully.")

    T0_fast_app = ToolFastApp(
        command_dict        = {"start": read_audio.start},
        get_status_function = read_audio.get_running,
        status_file         = "Tools/T0_ReadAudio/fast_com/status.txt",
        command_file        = "Tools/T0_ReadAudio/fast_com/command.txt"
    )

    logging.info("ReadAudio process started successfully.")

    T0_fast_app.run()