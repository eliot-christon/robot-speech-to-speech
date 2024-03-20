from faster_whisper import WhisperModel


class SpeechToText:
    """Class for real-time speech transcription from live wav file using a pre-trained audio model."""

    def __init__(self, model_size:str, input_wav_file:str, output_text_file:str):
        self.__wav_file = input_wav_file
        self.__text_file = output_text_file
        self.initialize_audio_model(model_size)
        self.__running = False
        self.__transcription = ""
    
    def initialize_audio_model(self, model:str):
        """Initialize the audio model with the given model size."""
        self.audio_model = WhisperModel(model, device="cuda", compute_type="float16")
    
    def get_running(self) -> bool:
        return self.__running
    
    def set_running(self, value:bool):
        self.__running = value

    def get_transcription(self) -> str:
        return self.__transcription

    def write_to_file(self):
        """Write the transcribed text to the output text file."""
        with open(self.__text_file, "w") as file:
            file.write(self.__transcription)

    def start(self):
        """Start the transcription process"""

        while self.__running:
            try:
                segments, info = self.audio_model.transcribe(self.__wav_file)
                text = "".join([segment.text for segment in segments])
                self.__transcription = text
                self.write_to_file()
                
            except Exception as e:
                pass
    
    def stop(self):
        """Stop the transcription process"""
        self.__running = False