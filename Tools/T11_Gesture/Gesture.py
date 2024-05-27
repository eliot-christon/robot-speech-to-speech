#-*- coding: utf-8 -*-
import naoqi
import logging
import qi
import time

class Gesture:
    """Class to control the Gestures with ALAnimationPlayer on the NAO robot"""

#%% CONSTRUCTOR ==========================================================================================================

    def __init__(self, nao_ip):
        self.__nao_ip = nao_ip
        self.__session = qi.Session()
        self.__session.connect("tcp://" + self.__nao_ip + ":9559")
        self.__gesture_service = self.__session.service("ALAnimationPlayer")
        self.__posture_service = self.__session.service("ALRobotPosture")
        self.__add_tags()
        self.__running = False
        self.__future = None

#%% METHODS ==============================================================================================================

    def __add_tags(self):
        tagToAnims = dict()
        tagToAnims["Toi"]      = ["animations/Sit/Gestures/You_4"]
        tagToAnims["Moi"]      = ["animations/Sit/Gestures/Me_7"]
        tagToAnims["Bonjour"]  = ["animations/Sit/Gestures/Hey_3"]
        tagToAnims["BodyTalk"] = ["animations/Sit/BodyTalk/BodyLanguage/BodyTalk_" + str(i) for i in range(1, 13)]
        tagToAnims["Attente"]  = ["animations/Sit/Waiting/PlayHands_1", "animations/Sit/Waiting/PlayHands_2", "animations/Sit/Waiting/PlayHands_3", "animations/Sit/Waiting/Relaxation_1", "animations/Sit/Waiting/Relaxation_2", "animations/Sit/Waiting/Relaxation_3", "animations/Sit/Waiting/ScratchBack_1", "animations/Sit/Waiting/ScratchHand_1", "animations/Sit/Waiting/ScratchHead_1", "animations/Sit/Waiting/ScratchLeg_1", "animations/Sit/Waiting/ScratchEye_1", "animations/Sit/Waiting/ScratchTorso_1", "animations/Sit/Waiting/Think_1", "animations/Sit/Waiting/Think_2", "animations/Sit/Waiting/Think_3", "animations/Sit/Waiting/Rest_1"]

        self.__gesture_service.addTagForAnimations(tagToAnims)

#%% GETTERS AND SETTERS ==================================================================================================

    def get_running(self):
        return self.__running

#%% COMMANDS =============================================================================================================

    def say_hi(self):
        self.__gesture_service.runTag("Bonjour")
        self.__gesture_service.runTag("Moi")

    def say_bye(self):
        self.__gesture_service.runTag("Bonjour")
        self.__posture_service.goToPosture("Sit", 0.5)

    def start(self):
        self.__running = True
        
        while self.__running:
            self.__future = self.__gesture_service.runTag("BodyTalk", _async=True)
            self.__future.wait()

        self.__running = False
    
    def stop(self):
        self.__running = False
        self.__future.cancel()
        logging.info("T11_Gesture: Finished.")
