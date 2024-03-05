import time
import logging

from SoundReceiverModule import SoundReceiverModule
from naoqi import ALProxy, ALBroker
from nao_ip import NAO_IP


HEXA_COLORS = {
    "red": 0x00FF0000,
    "dark_red": 0x00800000,
    "green": 0x0000FF00,
    "dark_green": 0x00008000,
    "blue": 0x000000FF,
    "dark_blue": 0x00000080,
    "cyan": 0x0000FFFF,
    "dark_cyan": 0x00008080,
    "magenta": 0x00FF00FF,
    "dark_magenta": 0x00800080,
    "yellow": 0x00FFFF00,
    "dark_yellow": 0x00808000,
    "white": 0xFFFFFFFF,
    "gray": 0x00808080,
    "black": 0x00000000
}


class NaoAssistant:
    """ Nao class for Nao robot """

    def __init__(self):
        self.atts = ALProxy(
            "ALAnimatedSpeech",
            NAO_IP,
            9559)
        self.tts = ALProxy(
            "ALTextToSpeech",
            NAO_IP,
            9559)
        self.speaking_movement = ALProxy(
            "ALSpeakingMovement",
            NAO_IP,
            9559)
        self.speaking_movement.setEnabled(True)
        self.speaking_movement.setMode("contextual")
        self.leds = ALProxy(
            "ALLeds",
            NAO_IP,
            9559)
        
        self.actions = {
            "resting": self.rest,
            "listening": self.listen,
            "speaking": self.speak
        }
        self.voices = {
            "fr" : "naofrf",
            "en" : "naoenu"
        }
        self.tts.setVoice(self.voices["fr"])
        self.current_state = ""


    def rest(self):
        """ Rest the Nao """
        self.write_state("resting")
        self.leds.fadeRGB("FaceLeds", HEXA_COLORS["dark_blue"], 0.5)

    def listen(self):
        """ Listen to the user """
        SoundReceiver.start()
        self.write_state("listening")
        self.leds.fadeRGB("FaceLeds", HEXA_COLORS["dark_green"], 0.5)
        # wait for the name to not be Nao
        while self.read_name() == "Nao":
            time.sleep(0.1)
    
    def speak(self):
        """ Speak to the user """
        # first get the message to say
        with open("py_com\\py311_msg_to_say.txt", "r") as f:
            msg_to_say = f.read()

        msg_to_say = msg_to_say.split(" ")[2:]
        msg_to_say = " ".join(msg_to_say)

        # get the language of the text stored in py311_language.txt
        with open("py_com\\py311_language.txt", "r") as f:
            lang = f.read()
        
        # check if the language is supported
        if lang not in self.voices.keys():
            lang = "fr"
        
        # set the language
        self.tts.setVoice(self.voices[lang])

        # then say it
        threadTts = self.atts.post.say(msg_to_say)
        self.write_state("speaking")
        self.leds.fadeRGB("FaceLeds", HEXA_COLORS["cyan"], 0.5)
        # wait for the end of the speech
        self.atts.wait(threadTts, 0)
    
    def write_state(self, state):
        """ Write the Nao state to a file """
        with open("py_com\\py27_robot_state.txt", "w") as f:
            f.write(state)
    
    def read_listen(self):
        """ Read the conversation state from a file """
        with open("py_com\\py311_listen.txt", "r") as f:
            return f.read() == "yes"
    
    def read_name(self):
        """ Read the message to say from a file """
        with open("py_com\\py311_msg_to_say.txt", "r") as f:
            msg = f.read()
        return msg.split(" ")[1][:-1]
    
    def next_state(self):
        """ Get the next state """
        name = self.read_name()
        listen = self.read_listen()

        if name == "Nao" and self.current_state != "speaking":
            return "speaking"
        elif listen:
            return "listening"
        else:
            return "resting"
        
    def start(self):
        """ Start the Nao assistant """
        self.atts.say("Bonjour, Je suis pret a demarrer une conversation.")

        next_state = self.current_state

        while True:
            try:

                next_state = self.next_state()

                if next_state != self.current_state:
                    logging.info("NaoClass: Changing state from {} to {}".format(self.current_state, next_state))
                    self.actions[next_state]()
                    self.current_state = next_state
                
                time.sleep(0.1)


            except KeyboardInterrupt:
                break
    
    def __del__(self):
        self.atts.say("Au revoir")
        self.write_state("resting")
        self.speaking_movement.setEnabled(False)
        self.leds.reset("AllLeds")


if __name__ == "__main__":

    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       NAO_IP,      # parent broker IP
       9559)        # parent broker port

    # Warning: SoundReceiver must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global SoundReceiver
    SoundReceiver = SoundReceiverModule(
        "SoundReceiver",
        NAO_IP,
        one_sentence=True,
        sentence_timeout=3,
        live_wav_each=10,
        wav_dir="py_com\\py27_audio.wav",
        save_csv=False,
    )

    nao = NaoAssistant()
    nao.start()

    nao.__del__()

    myBroker.shutdown()