# -*- coding: utf-8 -*-
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



# def msg_to_phrases(msg):
#     """ Convert a message to phrases """
#     phrases = []
#     phrase = ""

#     for submsg1 in msg.split("."):
#         for submsg2 in submsg1.split("?"):
#             for submsg3 in submsg2.split("!"):
#                 phrase += submsg3
#                 if len(phrase) > 0:
#                     phrases.append(phrase)
#                     phrase = ""
            
#     return phrases
import re


def msg_to_phrases(msg):
    """ Convert a message to phrases """
    phrases = []
    current_phrase = ""

    ponctuation_marks = [".", "!", "?", '...', ':', ',']
    pattern = '(' + '|'.join(re.escape(p) for p in ponctuation_marks) + ')'

    # Split the message by punctuation marks
    for sentence in re.split(pattern, msg):
        if sentence.strip():  # Check if the sentence is not empty
            if sentence.endswith(tuple(ponctuation_marks)):
                current_phrase += sentence.strip()
                if len(current_phrase) > 2:
                    phrases.append(current_phrase)
                current_phrase = ""
            else:
                current_phrase += sentence.strip()
    
    return phrases, current_phrase

# print(msg_to_phrases("Pour tenter d'attraper l'escroc dans son propre piege : 'Bonjour [Nom], je suis ravi de recevoir votre message. Cependant, il serait judicieux pour moi d'organiser un meeting avec vous afin que nous puissions discuter en détail des opportunités offertes par notre entreprise.'."))



class NaoAssistant:
    """ Nao class for Nao robot """

    def __init__(self, sound_receiver):
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
        self.sound_receiver = sound_receiver
        self.phrases_said = []
        self.phrases_to_say = []
        self.last_hour = ""


    def rest(self):
        """ Rest the Nao """
        self.write_state("resting")
        self.leds.fadeRGB("FaceLeds", HEXA_COLORS["dark_blue"], 0.5)

    def listen(self):
        """ Listen to the user """
        self.sound_receiver.start()
        self.write_state("listening")
        self.leds.fadeRGB("FaceLeds", HEXA_COLORS["dark_green"], 0.5)
        # wait for the end of the listening
        while not self.sound_receiver.is_stoped():
            time.sleep(0.05)
    
    def speak(self):
        """ Speak to the user """

        print("phrases to_say / said: ", len(self.phrases_to_say), "/", len(self.phrases_said))

        msg_to_say = " ".join(self.phrases_to_say)
        self.phrases_said += self.phrases_to_say

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
    
    def read_hour_name_and_message(self):
        """ Read the message to say from a file """
        with open("py_com\\py311_msg_to_say.txt", "r") as f:
            msg = f.read()
        if msg.split(" ").__len__() < 3:
            if msg.split(" ").__len__() == 1:
                return  msg.split(" ")[0], "", ""
            else:
                return  msg.split(" ")[0], msg.split(" ")[1], ""
        return  msg.split(" ")[0], msg.split(" ")[1][:-1], " ".join(msg.split(" ")[2:])
    
    def next_state(self):
        """ Get the next state """
        hour, name, msg = self.read_hour_name_and_message()
        listen = self.read_listen()

        if name == "Nao":

            if hour != self.last_hour:
                self.last_hour = hour
                self.phrases_said = []
            
            self.phrases_to_say = msg_to_phrases(msg)[0][len(self.phrases_said):]

            if len(self.phrases_to_say) > 0:
                if self.current_state == "speaking":
                    return "resting"
                return "speaking"

        else :
            self.phrases_said = []

        if listen:
            return "listening"
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
        posture = ALProxy("ALRobotPosture", NAO_IP, 9559)
        posture.post.goToPosture("Sit", 0.5)
        self.atts.say("Au revoir")
        self.write_state("resting")
        self.speaking_movement.setEnabled(False)
        self.leds.reset("AllLeds")