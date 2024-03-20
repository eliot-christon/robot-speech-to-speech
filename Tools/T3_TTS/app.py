from flask import Flask, jsonify
from threading import Thread
from TextToSpeech import TextToSpeech
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
def start_TTS():
    global text_to_speech
    
    if not text_to_speech.get_running():
        # Start TTS process in a separate thread
        TTS_thread = Thread(target=text_to_speech.start)
        TTS_thread.start()
        
        return jsonify({'message': 'TTS started successfully.'}), 200
    else:
        return jsonify({'message': 'TTS is already running.'}), 400


@app.route('/status', methods=['GET'])
def get_TTS_status():
    global text_to_speech
    
    if text_to_speech:
        status = text_to_speech.get_running()
        return jsonify({'status': status}), 200
    else:
        return jsonify({'message': 'No TTS process running.'}), 400

if __name__ == '__main__':

    # Set up the logging configuration
    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    logging.info("Starting the Text-to-Speech API server...")

    # Load the configuration parameters from the config file
    params = load_yaml("Tools/parameters.yaml")["T3_TTS"]

    # Initialize the TextToSpeech object
    text_to_speech = TextToSpeech(
        model_name = params["model_name"],
        input_text_file = params["input_text_file"],
        output_wav_file = params["output_wav_file"],
        speaker_wav_file = params["speaker_wav_file"],
        language = params["language"]
    )
    logging.info("Text-to-Speech object initialized successfully.")

    app.run(debug=True, port=params["port"])