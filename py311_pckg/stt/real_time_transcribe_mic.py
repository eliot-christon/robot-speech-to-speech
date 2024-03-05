import argparse
import os
import numpy as np
import speech_recognition as sr
from faster_whisper import WhisperModel
from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform


class SpeechTranscriber:
    """Class for real-time speech transcription using a microphone and a pre-trained audio model."""

    def __init__(self, model:str="small", energy_threshold:int=1000, record_timeout:float=2, phrase_timeout:float=3):
        # saving the parameters
        self.record_timeout = record_timeout
        self.phrase_timeout = phrase_timeout
        # local variables
        self.last_recording_time = None
        self.transcription = ['']
        self.data_queue = Queue()
        self.source = sr.Microphone(sample_rate=16000)
        # initializing the recorder and the audio model
        self.initialize_recorder(energy_threshold)
        self.initialize_audio_model(model)

    def initialize_recorder(self, energy_threshold:int):
        """Initialize the recorder with the given energy threshold."""
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = energy_threshold
        self.recorder.dynamic_energy_threshold = False
        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)
    
    def initialize_audio_model(self, model:str):
        """Initialize the audio model with the given model size."""
        self.audio_model = WhisperModel(model, device="cuda", compute_type="float16")
        print("Audio STT model initialized")
    
    def restet_variables(self):
        """Reset the variables to their initial state."""
        self.last_recording_time = None
        self.transcription = ['']
        self.data_queue = Queue()

    def start_transcribing(self, stop_after_one_phrase:bool=False):
        """Start the transcription process and return the transcribed text."""

        self.restet_variables()

        def record_callback(_, audio: sr.AudioData) -> None:
            """Callback function for the recorder to store the audio data in the queue."""
            data = audio.get_raw_data() # get the raw audio data (bytes)
            self.data_queue.put(data)   # put the data in the queue

        # start the recorder and the transcription process, this function is non-blocking and will call the callback function when it detects input from the source
        stop_listening = self.recorder.listen_in_background(self.source, record_callback, phrase_time_limit=self.record_timeout)

        # loop variables initialization
        old_queue_size = self.data_queue.qsize()
        text = ""
        running = True

        print("Listening for speech...") # let the user know that the system is ready to listen

        while running:

            try:
                now = datetime.utcnow() # get the current time

                # check if the phrase timeout has been reached
                if self.last_recording_time and now - self.last_recording_time > timedelta(seconds=self.phrase_timeout):
                    if text != "":                          # if there is a transcription, add it to the list
                        self.transcription.append(text)
                        if stop_after_one_phrase:           # if the stop_after_one_phrase flag is set, stop the transcription process
                            running = False
                    
                    self.data_queue.queue.clear()           # clear the queue
                    self.last_recording_time = now          # reset the last recording time
                    text = ""                               # reset the transcription

                new_info = self.data_queue.qsize() != old_queue_size
                if new_info and running:
                    # if there is new data in the queue and the transcription process is still running
                    old_queue_size = self.data_queue.qsize()
                    self.last_recording_time = now
                    audio_data = b''.join(self.data_queue.queue)                                        # get the audio data from the queue
                    audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0   # convert the audio data to a numpy array and normalize it
                    segments, _ = self.audio_model.transcribe(audio_np, beam_size=5)                    # transcribe the audio data using the audio model
                    text = "".join([segment.text for segment in segments])                              # get the transcription from the segments
                    self.transcription[-1] = text                                                       # update the last transcription in the list (until the phrase timeout is reached)

                    # Print the transcription.
                    if not stop_after_one_phrase:
                        os.system('cls' if platform == 'win32' else 'clear')
                        for line in self.transcription:
                            print(line)
                        print('', end='', flush=True)
                    else:
                        print("\r" + text, end="")
                    sleep(0.1) # infinite loops are bad, let's give the CPU a break
            
            except KeyboardInterrupt:
                # if the user interrupts the process, stop the transcription and print the final transcription
                print("\n\nTranscription:")
                text = "\n".join(self.transcription)
                print(text)
                running = False

        # stop the recorder by stopping the background listening
        stop_listening(wait_for_stop=False)
        
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
