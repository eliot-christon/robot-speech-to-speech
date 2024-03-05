from text_generation.Profiles import Human
from text_generation.Message import Message
from stt.real_time_transcribe_2 import SpeechTranscriber


class HumanSpeaker(Human):
    def __init__(self, name: str = "Pierre", mood: str = "neutre", work: str = "Pacte Novation", **kwargs):
        super().__init__(name, mood, work)
        self.transcriber = SpeechTranscriber(**kwargs)

    def describe(self, for_other: bool = False):
        return super().describe(for_other)

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return "HumanSpeaker(name={}, mood={}, work={})".format(self.name, self.mood, self.work)

    def write_listen(self, listen:bool):
        """ Write the conversation state to a file """
        with open("py_com\\py311_listen.txt", "w") as f:
            f.write("yes" if listen else "no")

    def __call__(self, prompt: str) -> Message:
        self.write_listen(True)
        response = self.transcriber.start_transcribing(stop_after_one_phrase=True)
        self.write_listen(False)
        return Message(self.name, response)
    
    def get_modelname(self) -> str:
        return "Audio_Model"

    def reset(self):
        self.write_listen(False)