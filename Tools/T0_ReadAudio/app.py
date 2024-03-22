import BaseHTTPServer
import json
from ReadAudio import ReadAudio
import logging
import yaml


class MyHttpRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def _set_response(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        if self.path == '/start':
            self._start_recording()
        elif self.path == '/stop':
            self._stop_recording()

    def do_GET(self):
        if self.path == '/status':
            self._get_recording_status()

    def _start_recording(self):
        global read_audio
        if not read_audio.get_running():
            # Start recording process in a separate thread
            read_audio.start()
            self._set_response(200)
            self.wfile.write(json.dumps({'message': 'ReadAudio started successfully.'}).encode())
        else:
            self._set_response(400)
            self.wfile.write(json.dumps({'message': 'ReadAudio is already running.'}).encode())


    def _get_recording_status(self):
        global read_audio
        if read_audio:
            status = read_audio.get_running()
            self._set_response(200)
            self.wfile.write(json.dumps({'status': status}).encode())
        else:
            self._set_response(400)
            self.wfile.write(json.dumps({'message': 'No ReadAudio process running.'}).encode())


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

    logging.info("Starting the ReadAudio API server...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")["T0_ReadAudio"]

    # Initialize the SpeechToText object
    read_audio = ReadAudio(
        nao_ip=params["nao_ip"],
        input_wav_file=params["input_wav_file"]
    )
    logging.info("ReadAudio object initialized successfully.")

    server_address = ('', params["port"])
    httpd = BaseHTTPServer.HTTPServer(server_address, MyHttpRequestHandler)
    logging.info("HTTP server started...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass