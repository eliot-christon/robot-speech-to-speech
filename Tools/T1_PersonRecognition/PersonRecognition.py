import logging
import time
from speechbrain.inference.encoders import MelSpectrogramEncoder
from torch import Tensor
import joblib
import torchaudio
import numpy as np

class PersonRecognition:
    """Class for person recognition"""

#%% CONSTRUCTOR ==========================================================================================================

    def __init__(self, output_text_file:str, input_audio_file:str, input_people_folder:str, input_model_dir:str, rejection_threshold:float=0.17):
        self.__text_file = output_text_file
        self.__audio_file = input_audio_file
        self.__people_folder = input_people_folder

        self.__embedding_model = MelSpectrogramEncoder.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb-mel-spec", savedir=input_model_dir + "spkrec-ecapa-voxceleb-mel-spec")
        self.__clf_model = joblib.load(input_model_dir + "person_recognition/speaker_verification_model.pkl")
        self.__labels = self.__clf_model.classes_
        self.__rejection_threshold = rejection_threshold

        self.__person_recognized = None
        self.__running = False
        self.__sleep_time = 0.03

#%% METHODS ==============================================================================================================

    def __write_to_file(self):
        """Write the output text to a file"""
        with open(self.__text_file, 'w', encoding='utf-8') as file:
            file.write(self.__person_recognized)
    
    def __load_audio(self, path:str) -> Tensor:
        """Load the audio file"""
        waveform, sample_rate = torchaudio.load(path)
        # resample to 16kHz if needed
        if sample_rate != 16000:
            waveform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(waveform)
        # convert to mono if needed
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        return waveform

    def __get_embedding(self, audio:Tensor) -> np.ndarray:
        """Get the embedding of the audio"""
        embedding = self.__embedding_model.encode_waveform(audio)
        return embedding.detach().numpy().reshape(1, -1)
    
    def __predict_with_rejection(self, probas:np.ndarray) -> str:
        """Predict the person with rejection"""
        if probas.max() < self.__rejection_threshold:
            return "Unknown"
        return self.__labels[probas.argmax()]

    def __train(self):
        """Train the model"""
        pass


#%% GETTERS AND SETTERS ==================================================================================================

    def get_running(self) -> bool:
        return self.__running
    
#%% START AND STOP ========================================================================================================

    def start(self):
        """Start the process"""

        self.__running = True

        while self.__running:

            self.__person_recognized = "Unknown"

            # Load the audio
            try:
                audio = self.__load_audio(self.__audio_file)
            except Exception as e:
                logging.error("T1_PersonRecognition: Error loading the audio file")
                time.sleep(self.__sleep_time)
                continue

            # Get the embedding
            try:
                embedding = self.__get_embedding(audio)
            except Exception as e:
                logging.error("T1_PersonRecognition: Error getting the embedding")
                time.sleep(self.__sleep_time)
                continue

            # Predict the person
            probas = self.__clf_model.predict_proba(embedding)
            self.__person_recognized = self.__predict_with_rejection(probas)

            logging.info("T1_PersonRecognition: Person recognized: " + self.__person_recognized)

            # Write the output to a file        
            self.__write_to_file()

            time.sleep(self.__sleep_time)
            self.__running = False

        logging.info("T1_PersonRecognition: Finished.")
