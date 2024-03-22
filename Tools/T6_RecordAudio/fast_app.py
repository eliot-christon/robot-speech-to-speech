import sys
import os
pckg_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(pckg_dir)

import logging
from SoundReceiverModule import SoundReceiverModule
from Tools.utils import ToolFastApp, load_yaml

if __name__ == '__main__':
    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    logging.info("Starting the RecordAudio API server...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")["T6_RecordAudio"]

    # Create a proxy to the NAO robot
    import naoqi
    myBroker = naoqi.ALBroker("myBroker",
                               "0.0.0.0",           # listen to anyone
                               0,                   # find a free port and use it
                               params["nao_ip"],    # parent broker IP
                               9559)                # parent broker port

    # Initialize the SoundReceiver object
    SoundReceiver = SoundReceiverModule(
        strModuleName="SoundReceiver",
        nao_ip=params["nao_ip"],
        output_wav_file=params["output_wav_file"],
        output_speech_detected_file=params["output_speech_detected_file"],
        channel=params["channel"],
        seconds_to_keep=params["seconds_to_keep"],
        sample_rate=params["sample_rate"],
        loudness_threshold=params["loudness_threshold"]
    )
    logging.info("RecordAudio object initialized successfully.")

    T6_fast_app = ToolFastApp(
        command_dict        = {"start": SoundReceiver.start, "stop": SoundReceiver.stop},
        get_status_function = SoundReceiver.get_running,
        status_file         = "Tools/T6_RecordAudio/fast_com/status.txt",
        command_file        = "Tools/T6_RecordAudio/fast_com/command.txt"
    )

    T6_fast_app.run()