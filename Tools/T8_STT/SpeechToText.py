from faster_whisper import WhisperModel
import logging
import time


class SpeechToText:
    """Class for real-time speech transcription from live wav file using a pre-trained audio model."""

#%% CONSTRUCTOR ==========================================================================================================

    def __init__(self, model_size:str, input_wav_file:str, output_text_file:str):
        self.__wav_file = input_wav_file
        self.__text_file = output_text_file
        self.initialize_audio_model(model_size)
        self.__running = False
        self.__transcription = ""

#%% METHODS ==============================================================================================================

    def initialize_audio_model(self, model:str):
        """Initialize the audio model with the given model size."""
        self.__audio_model = WhisperModel(model, device="cuda", compute_type="float16")

    def __write_to_file(self):
        """Write the transcribed text to the output text file."""
        with open(self.__text_file, "w", encoding='utf-8') as file:
            file.write(self.__transcription)

#%% GETTERS AND SETTERS ==================================================================================================

    def get_running(self) -> bool:
        return self.__running

    def get_transcription(self) -> str:
        return self.__transcription

#%% START AND STOP =======================================================================================================

    def start(self):
        """Start the transcription process"""

        logging.info("SpeechToText: Starting the transcription process...")

        self.__running = True

        while self.__running:
            try:
                segments, info = self.__audio_model.transcribe(self.__wav_file)
                text = "".join([segment.text for segment in segments])
                self.__transcription = text
                self.__write_to_file()
                time.sleep(0.2)

                
            except Exception as e:
                pass
    
    def stop(self):
        """Stop the transcription process"""
        logging.info("SpeechToText: Stopping the transcription process...")
        self.__running = False