import sys
import os
pckg_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(pckg_dir)

import logging
from .SoundReceiverModule import SoundReceiverModule
from ..utils import ToolFastApp, load_yaml, log_config

if __name__ == '__main__':

    log_config()
    
    logging.info("Starting the T6_RecordAudio process...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")
    nao_ip = params["nao_ip"]
    params = params["T6_RecordAudio"]

    # Create a proxy to the NAO robot
    import naoqi
    myBroker = naoqi.ALBroker("myBroker",
                               "0.0.0.0",           # listen to anyone
                               0,                   # find a free port and use it
                               nao_ip,              # parent broker IP
                               9559)                # parent broker port

    # Initialize the SoundReceiver object
    SoundReceiver = SoundReceiverModule(
        strModuleName="SoundReceiver",
        nao_ip=nao_ip,
        output_wav_file=params["output_wav_file"],
        output_speech_detected_file=params["output_speech_detected_file"],
        channel=params["channel"],
        seconds_to_keep=params["seconds_to_keep"],
        sample_rate=params["sample_rate"],
        loudness_threshold=params["loudness_threshold"]
    )
    logging.info("T6_RecordAudio object initialized successfully.")

    T6_fast_app = ToolFastApp(
        command_dict        = {"start": SoundReceiver.start, "stop": SoundReceiver.stop},
        get_status_function = SoundReceiver.get_running,
        status_file         = "Tools/T6_RecordAudio/fast_com/status.txt",
        command_file        = "Tools/T6_RecordAudio/fast_com/command.txt"
    )

    T6_fast_app.run()