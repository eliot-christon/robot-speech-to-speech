#-*- coding: utf-8 -*-
import naoqi
import logging
import time

class Gesture:
    """Class to control the Gestures with ALAnimationPlayer on the NAO robot"""

#%% CONSTRUCTOR ==========================================================================================================

    def __init__(self, nao_ip, input_text_file):
        self.__nao_ip = nao_ip
        self.__input_tag_file = input_text_file
        self.__gesture_proxy = naoqi.ALProxy("ALAnimationPlayer", self.__nao_ip, 9559)
        self.__posture_proxy = naoqi.ALProxy("ALRobotPosture", self.__nao_ip, 9559)
        self.__leds_proxy = naoqi.ALProxy("ALLeds", self.__nao_ip, 9559)
        self.__tags = []
        self.__add_tags()
        self.__running = False

#%% METHODS ==============================================================================================================

    def __add_tags(self):
        tagToAnims = dict()
        tagToAnims["Toi"]      = ["animations/Sit/Gestures/You_4"]
        tagToAnims["Moi"]      = ["animations/Sit/Gestures/Me_7"]
        tagToAnims["Bonjour"]  = ["animations/Sit/Gestures/Hey_3"]
        tagToAnims["BodyTalk"] = ["animations/Sit/BodyTalk/BodyLanguage/BodyTalk_" + str(i) for i in range(1, 13)]
        tagToAnims["Attente"]  = ["animations/Sit/Waiting/PlayHands_1", "animations/Sit/Waiting/PlayHands_2", "animations/Sit/Waiting/PlayHands_3", "animations/Sit/Waiting/Relaxation_1", "animations/Sit/Waiting/Relaxation_2", "animations/Sit/Waiting/Relaxation_3", "animations/Sit/Waiting/ScratchBack_1", "animations/Sit/Waiting/ScratchHand_1", "animations/Sit/Waiting/ScratchHead_1", "animations/Sit/Waiting/ScratchLeg_1", "animations/Sit/Waiting/ScratchEye_1", "animations/Sit/Waiting/ScratchTorso_1", "animations/Sit/Waiting/Think_1", "animations/Sit/Waiting/Think_2", "animations/Sit/Waiting/Think_3", "animations/Sit/Waiting/Rest_1"]

        self.__gesture_proxy.addTagForAnimations(tagToAnims)

        self.__tags = list(tagToAnims.keys())
    
    def __read_tag(self):
        with open(self.__input_tag_file, 'r') as file:
            return file.read()

#%% GETTERS AND SETTERS ==================================================================================================

    def get_running(self):
        return self.__running

#%% COMMANDS =============================================================================================================

    def start(self):
        self.__running = True
        while self.__running:
            tag = self.__read_tag()
            if tag in self.__tags:
                self.__gesture_proxy.runTag(tag)
            else:
                logging.error("T11_Gesture: Tag not found: " + tag)
                time.sleep(0.1)
            
    
    def stop(self):
        self.__posture_proxy.goToPosture("Sit", 0.5)
        self.__leds_proxy.reset("AllLeds")
        self.__running = False
        logging.info("T11_Gesture: Finished.")
