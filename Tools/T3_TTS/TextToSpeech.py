import logging
import torch
from TTS.api import TTS
from extract_num import extract_numbers
from enlettres import enlettres

class TextToSpeech:
    """Class for real-time speech TTS from live wav file using a pre-trained audio model."""

#%% CONSTRUCTOR ==========================================================================================================

    def __init__(self, model_name:str, language:str, input_text_file:str, output_wav_file:str, speaker_wav_file:str):
        self.__text_file = input_text_file
        self.__wav_file = output_wav_file
        self.__speaker_wav = speaker_wav_file
        self.__language = language

        self.__running = False
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.__tts = TTS(model_name).to(device)

#%% METHODS ==============================================================================================================

    def __treat_text(self, text:str) -> str:
        """Treat the text before synthesis"""
        # numbers
        numbers = extract_numbers(text)
        if numbers:
            for num in numbers:
                text = text.replace(str(num), enlettres(num))
        # symbols
        text = text.replace("&", "et")
        text = text.replace("€", "euros")
        text = text.replace("°", "degrés")
        text = text.replace("%", "pour cent")
        text = text.replace("£", "livres")
        text = text.replace("¥", "yens")
        text = text.replace("#", "hashtag")
        text = text.replace("@", "arobase")
        text = text.replace("«", "")
        text = text.replace("»", "")
        # exceptions
        text = text.replace("est - ce", "est-ce")
        # operations
        text = text.replace("+", "plus")
        text = text.replace(" - ", " moins ")
        text = text.replace(" * ", " fois ")
        text = text.replace(" / ", " divisé par ")
        # ponctuation
        text = text.replace(" ?", "?")
        text = text.replace(" !", "!")
        text = text.replace(" .", ".")
        text = text.replace(" ,", ",")
        text = text.replace(" ;", ";")
        # site
        text = text.replace("www.", "trois w point ")
        text = text.replace(".com", " point com")
        # others
        text = text.replace("  ", " ")
        text = text.replace("etc.", "et cetera.")
        return text

    def __read_text(self) -> str:
        """Read the input text file and return the text as string"""
        with open(self.__text_file, 'r', encoding='utf-8') as file:
            text = file.read().replace('\n', '')
        return text

#%% GETTERS AND SETTERS ==================================================================================================

    def get_running(self) -> bool:
        return self.__running
    
    def get_wav_file(self) -> str:
        return self.__wav_file
    
    def set_wav_file(self, wav_file:str):
        self.__wav_file = wav_file

    def get_text_file(self) -> str:
        return self.__text_file

    def set_text_file(self, text_file:str):
        self.__text_file = text_file

    def get_speaker_wav(self) -> str:
        return self.__speaker_wav
    
    def set_speaker_wav(self, speaker_wav:str):
        self.__speaker_wav = speaker_wav
    

#%% START ================================================================================================================

    def start(self):
        """Start the TTS process"""

        self.__running = True

        text = self.__read_text()
        text = self.__treat_text(text)

        if not text:
            logging.error("SpeechToText: No text to synthesize.")
            self.__running = False
            return

        # Generate the speech directly to a file
        if "multilingual" in self.__tts.model_name:
            self.__tts.tts_to_file(
                text        = text,
                file_path   = self.__wav_file,
                language    = self.__language,
                speaker_wav = self.__speaker_wav
            )
        else:
            self.__tts.tts_to_file(
                text      = text,
                file_path = self.__wav_file
            )

        self.__running = False

        logging.info("TextToSpeech: Finished.")
