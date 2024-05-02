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
        self.__list_nothing_saids = [
            " Thank you for watching.",
            " Thanks for watching!",
            " Thank you for watching.",
            " Thank you.",
            " Thank you. Bye.",
            " ...",
            " Merci d'avoir regardé cette vidéo !",
            " Please subscribe to my channel.",
            " If you enjoyed this video, please like, comment, subscribe, and share it with your friends.",
            "ご視聴ありがとうございました",
            "最後まで視聴してくださって 本当にありがとうございます",
            " 다음 영상에서 만나요!",
            " 수고하셨습니다.",
            "好",
            " MBC 뉴스 이재경입니다.",
            " Ah!",
        ]

#%% METHODS ==============================================================================================================

    def initialize_audio_model(self, model:str):
        """Initialize the audio model with the given model size."""
        self.__audio_model = WhisperModel(model, device="cuda", compute_type="float16")
    
    def __nothing_said(self, text:str) -> bool:
        """Check if the transcribed text is one of the predefined 'nothing said' phrases."""
        if text in self.__list_nothing_saids:
            return True
        return False

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

        self.__running = True

        while self.__running:
            try:
                segments, info = self.__audio_model.transcribe(self.__wav_file)
                text = "".join([segment.text for segment in segments])
                if self.__nothing_said(text):
                    text = ""
                self.__transcription = text
                self.__write_to_file()
                time.sleep(0.1)

            except Exception as e:
                logging.error(f"SpeechToText: {e}")
        
        logging.info("SpeechToText: Finished.")
    
    def stop(self):
        """Stop the transcription process"""
        self.__running = False
