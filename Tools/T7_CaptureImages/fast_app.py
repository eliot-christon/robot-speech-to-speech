import sys
import os
pckg_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(pckg_dir)

import logging
from .CaptureImages import CaptureImages
from ..utils import ToolFastApp, load_yaml, log_config

if __name__ == '__main__':

    log_config()

    logging.info("Starting the T7_CaptureImages process...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")
    nao_ip = params["nao_ip"]
    params = params["T7_CaptureImages"]

    # Initialize the CaptureImages object
    capture_images = CaptureImages(
        nao_ip                  = nao_ip,
        output_image_folder     = params["output_image_folder"],
        video_device_args       = params["video_device_args"],
        face_detection_time_ms  = params["face_detection_time_ms"],
        image_args              = params["image_args"],
        interval                = params["interval"],
        number_of_images        = params["number_of_images"]
    )
    logging.info("T7_CaptureImages object initialized successfully.")

    T7_fast_app = ToolFastApp(
        command_dict        = {"start": capture_images.start, "stop": capture_images.stop},
        get_status_function = capture_images.get_running,
        status_file         = "Tools/T7_CaptureImages/fast_com/status.txt",
        command_file        = "Tools/T7_CaptureImages/fast_com/command.txt"
    )

    T7_fast_app.run()