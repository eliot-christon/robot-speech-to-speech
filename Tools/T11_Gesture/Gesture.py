#-*- coding: utf-8 -*-
import naoqi
import logging
import random

class Gesture:
    """Class to control the Gestures with ALAnimationPlayer on the NAO robot"""

#%% CONSTRUCTOR ==========================================================================================================

    def __init__(self, nao_ip):
        self.__nao_ip = nao_ip
        self.__gesture_proxy = naoqi.ALProxy("ALAnimationPlayer", self.__nao_ip, 9559)
        self.__running = False

#%% METHODS ==============================================================================================================

#%% GETTERS AND SETTERS ==================================================================================================

    def get_running(self):
        return self.__running

#%% COMMANDS =============================================================================================================

    def start(self):
        self.__running = True
        while self.__running:
            # get random number between 1 and 10
            random_number = random.randint(1, 10)
            # play the animation
            self.__gesture_proxy.run("animations/Sit/BodyTalk/BodyTalk_" + str(random_number))
    
    def stop(self):
        self.__running = False
        logging.info("T11_Gesture: Finished.")
        self.__gesture_proxy.reset()
