#-*- coding: utf-8 -*-
import naoqi

class Leds:
    """Class to control the LEDs on the NAO robot"""

#%% CONSTRUCTOR ==========================================================================================================

    def __init__(self, nao_ip, input_text_file):
        self.__nao_ip = nao_ip
        self.__text_file = input_text_file

        self.__leds_proxy = naoqi.ALProxy("ALLeds", self.__nao_ip, 9559)
        self.__running = False

#%% METHODS ==============================================================================================================

    def __read_file(self):
        with open(self.__text_file, "r") as file:
            return file.read()

#%% GETTERS AND SETTERS ==================================================================================================

    def get_running(self):
        return self.__running

#%% COMMANDS =============================================================================================================

    def start(self):
        self.__running = True
        rgb = self.__read_file()
        self.__leds_proxy.fadeRGB("FaceLeds", rgb, 0.5)
        self.__running = False

    def reset(self):
        self.__leds_proxy.reset("FaceLeds")