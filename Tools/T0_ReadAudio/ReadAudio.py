#-*- coding: utf-8 -*-
import naoqi
import logging
import paramiko
import time

class ReadAudio:
    """Class to read audio file on NAO robot"""

#%% CONSTRUCTOR ==========================================================================================================

    def __init__(self, nao_ip, input_wav_file, nao_username="nao", nao_password="nao"):
        self.__nao_ip = nao_ip
        self.__wav_file = input_wav_file
        self.__nao_username = nao_username
        self.__nao_password = nao_password

        self.audio_player = naoqi.ALProxy("ALAudioPlayer", self.__nao_ip, 9559)
        self.__robot_file = "/home/nao/audio_generated.wav"
        self.__running = False

#%% METHODS ==============================================================================================================

    def __upload_file(self):
        transport = paramiko.Transport((self.__nao_ip, 22))
        transport.connect(username=self.__nao_username, password=self.__nao_password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(self.__wav_file, self.__robot_file)
        sftp.close()
        transport.close()

#%% GETTERS AND SETTERS ==================================================================================================

    def get_running(self):
        return self.__running
    
    def get_wav_file(self):
        return self.__wav_file
    
    def set_wav_file(self, wav_file):
        self.__wav_file = wav_file

    def get_robot_file(self):
        return self.__robot_file

#%% START ================================================================================================================

    def start(self):
        """Start the audio reading process"""

        self.__running = True

        self.__upload_file()

        try:
            self.audio_player.playFile(self.__robot_file)
        except Exception as e:
            logging.error("ReadAudio: Error playing audio file on NAO robot")
            time.sleep(1)
            # try again
            self.audio_player.playFile(self.__robot_file)

        self.__running = False

        logging.info("ReadAudio: Finished.")
    