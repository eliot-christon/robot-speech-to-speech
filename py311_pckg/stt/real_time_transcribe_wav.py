import argparse
from faster_whisper import WhisperModel
from time import sleep
import wave


class SpeechTranscriber:
    """Class for real-time speech transcription from live wav file using a pre-trained audio model."""

    def __init__(self, model="small", raw_filepath="py_com\\py27_audio.wav"):
        self.raw_file_path = raw_filepath
        self.initialize_audio_model(model)
    
    def initialize_audio_model(self, model:str):
        """Initialize the audio model with the given model size."""
        self.audio_model = WhisperModel(model, device="cuda", compute_type="float16")
        print("Audio STT model initialized")
    
    def read_listen(self):
        """ Read the conversation state from a file """
        with open("py_com\\py27_listen.txt", "r") as f:
            return f.read() == "yes"
    
    def write_language(self, language:str):
        """ Write the language to a file """
        with open("py_com\\py311_language.txt", "w") as f:
            f.write(language)

    def start_transcribing(self, stop_after_one_phrase=False):
        """Start the transcription process and return the transcribed text."""
        
        text = ""
        running = True

        sleep(0.05)

        print("Waiting for listenning flag...", end="")

        while not self.read_listen():
            sleep(0.1)

        print("\rListening for speech...            ")

        while running:
            try:
                segments, info = self.audio_model.transcribe(self.raw_file_path)
                text = "".join([segment.text for segment in segments])
                if stop_after_one_phrase and not self.read_listen():
                    running = False
                print("\rTEXT:", text, end="                            ")
                sleep(0.1)
            except KeyboardInterrupt:
                print("\n\nTranscription:")
                print(text)
                running = False
            except Exception as e:
                print("\n\nError:", e, "\n")
        
        if stop_after_one_phrase:
            # Empty the wav file
            print()
            empty_wav = wave.open(self.raw_file_path, "w")
            empty_wav.setnchannels(1)
            empty_wav.setsampwidth(2)
            empty_wav.setframerate(48000)
            empty_wav.writeframes(b'')
            empty_wav.close()

        if info:
            self.write_language(info.language)

        return text
        


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="medium", help="Model to use",
                        choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--energy_threshold", default=1000,
                        help="Energy level for mic to detect.", type=int)
    parser.add_argument("--record_timeout", default=2,
                        help="How real time the recording is in seconds.", type=float)
    parser.add_argument("--phrase_timeout", default=3,
                        help="How much empty space between recordings before we "
                             "consider it a new line in the transcription.", type=float)

    args = parser.parse_args()
    transcriber = SpeechTranscriber(args.model, args.energy_threshold,
                                    args.record_timeout, args.phrase_timeout)
    transcriber.start_transcribing()


if __name__ == "__main__":
    main()
