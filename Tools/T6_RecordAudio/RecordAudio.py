import naoqi
import numpy as np
import time
import sys
import os
import logging
import wave


class RecordAudio(naoqi.ALModule):
    """
    Use this object to get call back from the ALMemory of the naoqi world.
    Your callback needs to be a method with two parameter (variable name, value).
    """

#%% CONSTRUCTOR AND DESTRUCTOR ============================================================================================

    def __init__(self, strModuleName, nao_ip, output_wav_file, output_speech_detected_file, channel, seconds_to_keep, sample_rate, loudness_threshold):
        
        naoqi.ALModule.__init__(self, strModuleName)
        self.BIND_PYTHON(self.getName(),"callback")
        self.__audio_proxy = naoqi.ALProxy("ALAudioDevice", nao_ip, 9559)

        self.__wav_file = output_wav_file
        self.__speech_detected_file = output_speech_detected_file
        self.__channel = channel
        self.__sample_rate = sample_rate
        self.__samples_to_keep = seconds_to_keep * sample_rate
        self.__loudness_threshold = loudness_threshold

        self.__running = False
        self.__aSoundData = None

    def __del__(self):
        """clean when module is destroyed"""
        logging.info("RecordAudio.__del__: cleaning everything")
        self.stop()

#%% METHODS ==============================================================================================================
    
    def __write_wav_to_file(self):
        """write the buffer to the wav file, only samples_to_keep samples are kept"""
        logging.debug("RecordAudio: writing to file")
        with open(self.__wav_file, 'ab') as file:
            # get the samples from the file
            all_samples = file.read()
            overflown_samples = len(all_samples) + len(self.__aSoundData[self.__channel]) - self.__samples_to_keep
            if overflown_samples > 0:
                # remove the oldest samples
                all_samples = all_samples[overflown_samples:]
                file.seek(0)
                file.write(all_samples)
            # write the new samples
            file.write(self.__aSoundData[self.__channel].tobytes())
    
    def __write_time_speech_detected_to_file(self):
        """write the current time to the file"""
        with open(self.__speech_detected_file, 'ab') as file:
            file.write("speech detected at: " + time.strftime("%c") + "\n")
    
    def __speechDetected(self):
        """return True if the given sound data is a speech"""
        # based on the mean loudness of both left and right channels (n1 and n3)
        n1 = self.__soundDataLoudness(self.__aSoundData[1])
        n3 = self.__soundDataLoudness(self.__aSoundData[3])
        return (n1 + n3) / 2 > self.__loudness_threshold
    

    def __soundDataLoudness(self, aSoundDataChannel):
        """compute the loudness of the given sound data, between 0 and 1"""
        return 1 - ( np.sqrt(np.mean(aSoundDataChannel**2)) / 100 )

#%% GETTERS AND SETTERS ==================================================================================================

    def get_running(self):
        return self.__running
    
    def get_channel(self):
        return self.__channel
    
    def set_channel(self, channel):
        self.__channel = channel
    
    def get_samples_to_keep(self):
        return self.__samples_to_keep
    
    def set_samples_to_keep(self, samples_to_keep):
        self.__samples_to_keep = samples_to_keep
    
    def get_loudness_threshold(self):
        return self.__loudness_threshold
    
    def set_loudness_threshold(self, loudness_threshold):
        self.__loudness_threshold = loudness_threshold

#%% START AND STOP =======================================================================================================

    def start(self, nNbrChannelFlag=0, nDeinterleave=0):
        """launch the listening process (this is a non blocking call)
        #nNbrChannelFlag    ALL_Channels: 0,  AL::LEFTCHANNEL: 1, AL::RIGHTCHANNEL: 2; AL::FRONTCHANNEL: 3  or AL::REARCHANNEL: 4."""
        # save the current configuration and subscribe to the audio device
        self.__audio_proxy.setClientPreferences(self.getName(),  self.__sample_rate, nNbrChannelFlag, nDeinterleave) # setting same as default generate a bug !?!
        self.__audio_proxy.subscribe(self.getName())

        self.__running = True

        logging.info("RecordAudio: started!")

    def stop(self):
        """stop the listening process"""

        self.__audio_proxy.unsubscribe(self.getName())
        self.__running = False

        logging.info("RecordAudio: stopped!")
    
#%% CALLBACK ============================================================================================================

    def processRemote(self, nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, buffer):
        """
        This is THE method that receives all the sound buffers from the "ALAudioDevice" module
        """
        print("RecordAudio: processRemote()")

        if not self.__running:
            return

        # reconstruct the 4 channels audio buffer
        aSoundDataInterlaced = np.fromstring(str(buffer), dtype=np.int16)
        self.__aSoundData = np.reshape(aSoundDataInterlaced, (nbOfChannels, nbrOfSamplesByChannel), 'F')

        # write to file
        self.__write_wav_to_file()

        if self.__speechDetected():
            self.__write_time_speech_detected_to_file()
