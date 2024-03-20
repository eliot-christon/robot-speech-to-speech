from flask import Flask, jsonify
from threading import Thread
from SpeechToText import SpeechToText
import logging
import yaml

app = Flask(__name__)


def load_yaml(file_path):
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as exc:
            logging.error(exc)


@app.route('/start', methods=['POST'])
def start_transcription():
    global speech_to_text
    
    if not speech_to_text.get_running():
        # Start transcription process in a separate thread
        transcription_thread = Thread(target=speech_to_text.start)
        transcription_thread.start()
        
        return jsonify({'message': 'Transcription started successfully.'}), 200
    else:
        return jsonify({'message': 'Transcription is already running.'}), 400

@app.route('/stop', methods=['POST'])
def stop_transcription():
    global speech_to_text
    
    if speech_to_text.get_running():
        # Stop transcription process
        speech_to_text.stop()
        
        return jsonify({'message': 'Transcription stopped successfully.'}), 200
    else:
        return jsonify({'message': 'No transcription process running.'}), 400

@app.route('/status', methods=['GET'])
def get_transcription_status():
    global speech_to_text
    
    if speech_to_text:
        status = speech_to_text.get_running()
        return jsonify({'status': status}), 200
    else:
        return jsonify({'message': 'No transcription process running.'}), 400

if __name__ == '__main__':

    # Set up the logging configuration
    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    logging.info("Starting the Speech-to-Text API server...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")["T8_STT"]

    # Initialize the SpeechToText object
    speech_to_text = SpeechToText(
        model_size=params["model_size"],
        input_wav_file=params["input_wav_file"],
        output_text_file=params["output_text_file"]
    )
    logging.info("Speech-to-Text object initialized successfully.")

    app.run(debug=True, port=params["port"])