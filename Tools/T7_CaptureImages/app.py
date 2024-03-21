import BaseHTTPServer
import json
from CaptureImages import CaptureImages
import logging
import yaml
import threading



class MyHttpRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def _set_response(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        if self.path == '/start':
            self._start_capturing()
        elif self.path == '/stop':
            self._stop_capturing()

    def do_GET(self):
        if self.path == '/status':
            self._get_capturing_status()

    def _start_capturing(self):
        global capture_images_thread
        if not capture_images_thread or not capture_images_thread.is_alive():
            # Start capturing process in a separate thread
            capture_images_thread = threading.Thread(target=capture_images.start)
            capture_images_thread.daemon = True
            capture_images_thread.start()
            self._set_response(200)
            self.wfile.write(json.dumps({'message': 'Capturing started successfully.'}).encode())
        else:
            self._set_response(400)
            self.wfile.write(json.dumps({'message': 'Capturing is already running.'}).encode())

    def _stop_capturing(self):
        global capture_images_thread
        if capture_images_thread and capture_images_thread.is_alive():
            # Stop capturing process
            capture_images.stop()
            capture_images_thread.join()  # Wait for the thread to terminate
            self._set_response(200)
            self.wfile.write(json.dumps({'message': 'Capturing stopped successfully.'}).encode())
        else:
            self._set_response(400)
            self.wfile.write(json.dumps({'message': 'No capturing process running.'}).encode())

    def _get_capturing_status(self):
        global capture_images_thread
        if capture_images_thread and capture_images_thread.is_alive():
            status = "running"
        else:
            status = "stopped"
        self._set_response(200)
        self.wfile.write(json.dumps({'status': status}).encode())


def load_yaml(file_path):
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as exc:
            logging.error(exc)


if __name__ == '__main__':
    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    logging.info("Starting the CaptureImages API server...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")["T7_CaptureImages"]

    # Initialize the CaptureImages object
    capture_images = CaptureImages(
        nao_ip                  = params["nao_ip"],
        output_image_folder     = params["output_image_folder"],
        video_device_args       = params["video_device_args"],
        face_detection_time_ms  = params["face_detection_time_ms"],
        image_args              = params["image_args"],
        interval                = params["interval"],
        number_of_images        = params["number_of_images"]
    )
    logging.info("CaptureImages object initialized successfully.")

    capture_images_thread = None

    server_address = ('', params["port"])
    httpd = BaseHTTPServer.HTTPServer(server_address, MyHttpRequestHandler)
    logging.info("HTTP server started...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass