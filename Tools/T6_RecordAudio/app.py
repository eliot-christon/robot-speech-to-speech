import BaseHTTPServer
import json
from SoundReceiverModule import SoundReceiverModule
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
        global SoundReceiver
        print("MyHttpRequestHandler: _start_recording()")
        if not SoundReceiver.get_running():
            # Start recording process in a separate thread
            SoundReceiver.start()
            self._set_response(200)
            self.wfile.write(json.dumps({'message': 'Recording started successfully.'}).encode())
        else:
            self._set_response(400)
            self.wfile.write(json.dumps({'message': 'Recording is already running.'}).encode())

    def _stop_recording(self):
        global SoundReceiver
        if SoundReceiver.get_running():
            # Stop recording process
            SoundReceiver.stop()
            self._set_response(200)
            self.wfile.write(json.dumps({'message': 'Recording stopped successfully.'}).encode())
        else:
            self._set_response(400)
            self.wfile.write(json.dumps({'message': 'No recording process running.'}).encode())

    def _get_recording_status(self):
        global SoundReceiver
        if SoundReceiver:
            status = SoundReceiver.get_running()
            self._set_response(200)
            self.wfile.write(json.dumps({'status': status}).encode())
        else:
            self._set_response(400)
            self.wfile.write(json.dumps({'message': 'No recording process running.'}).encode())


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

    # Initialize the SpeechToText object
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

    server_address = ('', params["port"])
    httpd = BaseHTTPServer.HTTPServer(server_address, MyHttpRequestHandler)
    logging.info("HTTP server started...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass