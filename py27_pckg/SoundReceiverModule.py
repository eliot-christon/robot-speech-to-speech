# Description: This script is used to retrieve the audio buffer from the NAO robot and save it

__author__ = "Eliot CHRISTON"
__version__ = "1.1"
__annotations__ = "Based on the work of Alexandre Mazel"


#%% IMPORTS ============================================================================================================

from nao_ip import NAO_IP

from optparse import OptionParser
import naoqi
import numpy as np
import time
import sys
import os
import logging
import wave
import pandas as pd


#%% CLASS ==============================================================================================================

class SoundReceiverModule(naoqi.ALModule):
    """
    Use this object to get call back from the ALMemory of the naoqi world.
    Your callback needs to be a method with two parameter (variable name, value).
    """

    def __init__(self,
                 strModuleName,
                 strNaoIp,
                 raw_dir="data\\audio\\raw\\",
                 wav_dir="data\\audio\\wav\\",
                 csv_dir="data\\audio\\csv\\",
                 live_wav_each=10, last=True,
                 one_sentence=False,
                 sentence_timeout=5,
                 loudness_threshold=0.5,
                 save_csv=True,
                 ):
        try:
            naoqi.ALModule.__init__(self, strModuleName)
            self.BIND_PYTHON(self.getName(),"callback")

            # saving the input parameters
            self.strNaoIp = strNaoIp                        # the IP of the NAO robot
            self.live_wav_each = live_wav_each              # save a wav file every live_wav_each iterations
            self.one_sentence = one_sentence                # if True, the module will stop after one sentence
            self.sentence_timeout = sentence_timeout        # the time to wait before considering a sentence as finished
            self.loudness_threshold = loudness_threshold    # the loudness threshold to consider a sound as a sentence
            self.save_csv = save_csv                        # if True, the module will save the data in csv files
            
            # directories
            self.raw_dir = raw_dir                          # the directory where the raw files will be saved
            self.wav_dir = wav_dir                          # the directory where the wav files will be saved
            self.csv_dir = csv_dir                          # the directory where the csv files will be saved

            # local variables
            self.started = False                            # if True, the module has been started
            self.count_for_live_wav_save = 0                # the count for the live wav save
            self.stop_csv_save = False                      # if True, the module will stop saving the data (for csv files)
            self.last_sound_above_loudness_threshold = None # the last time a sound was above the loudness threshold
            self.at_least_one_sound = False                 # if at least one sound has been detected
            self.dfs = [pd.DataFrame(columns=[              # the dataframes for the csv files
                "aTimeStamp", 
                "audio", 
                "frequency", 
                "loudness"])] * 4
            if last:
                self.date_and_time = "last"
            else:
                self.date_and_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
            
            self.audio_proxy = naoqi.ALProxy("ALAudioDevice", self.strNaoIp, 9559)
            
            # Output files (ASSUME nb channels = 4)
            self.aOutfile = [None]*4    # audio

        except BaseException as err:
            logging.error("SoundReceiverModule: loading error: %s" % str(err))


    def __del__(self):
        """clean when module is destroyed"""
        logging.info("SoundReceiverModule.__del__: cleaning everything")
        self.stop()

    
    def write_listen(self, listen):
        """ Write the conversation state to a file """
        with open("py_com\\py27_listen.txt", "w") as f:
            f.write("yes" if listen else "no")


    def start(self, nNbrChannelFlag=0, nDeinterleave=0, nSampleRate=48000):
        """launch the listening process (this is a non blocking call)
        #nNbrChannelFlag    ALL_Channels: 0,  AL::LEFTCHANNEL: 1, AL::RIGHTCHANNEL: 2; AL::FRONTCHANNEL: 3  or AL::REARCHANNEL: 4."""

        # save the current configuration and subscribe to the audio device
        self.audio_proxy.setClientPreferences(self.getName(),  nSampleRate, nNbrChannelFlag, nDeinterleave) # setting same as default generate a bug !?!
        self.audio_proxy.subscribe(self.getName())

        self.started = True
        self.write_listen(True)

        logging.info("SoundReceiverModule: started!")


    def stop(self):
        """stop the listening process"""
        logging.info("SoundReceiverModule: stopping...")

        self.started = False
        self.write_listen(False)

        # close files if needed
        if(self.aOutfile != [None]*4):
            for channel_number in range(0, 4):
                self.aOutfile[channel_number].close()
                self.aOutfile[channel_number] = None

        # unsubscribe from the ALAudioDevice (stop listening)
        # self.audio_proxy.unsubscribe(self.getName())
        # print("audio_proxy.unsubscribe(self.getName()) done!")

        logging.info("SoundReceiverModule: stopped!")
    
    
    def is_stoped(self):
        """return True if the module is stopped"""
        return not self.started


    def speechDetected(self, aSoundData):
        """return True if the given sound data is a speech"""
        # based on the mean loudness of both left and right channels (n1 and n3)
        n1 = self.soundDataLoudness(aSoundData[1])
        n3 = self.soundDataLoudness(aSoundData[3])
        return (n1 + n3) / 2 > self.loudness_threshold
    

    def soundDataLoudness(self, aSoundDataChannel):
        """compute the loudness of the given sound data, between 0 and 1"""
        return 1 - ( np.sqrt(np.mean(aSoundDataChannel**2)) / 100 )
    

    def soundDataFrequency(self, aSoundDataChannel):
        """compute the frequency of the given sound data"""
        return np.abs(np.fft.fft(aSoundDataChannel))
    

    def processRemote(self, nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, buffer):
        """
        This is THE method that receives all the sound buffers from the "ALAudioDevice" module
        """

        if not self.started:
            return

        # reconstruct the 4 channels audio buffer
        aSoundDataInterlaced = np.fromstring(str(buffer), dtype=np.int16)
        aSoundData = np.reshape(aSoundDataInterlaced, (nbOfChannels, nbrOfSamplesByChannel), 'F')

        # now save each channel in a different raw file
        for channel_number in range(0, nbOfChannels):

            # create a new file if needed
            if self.aOutfile[channel_number] == None:
                logging.info("SoundReceiverModule: creating file for channel %s" % channel_number)
                self.aOutfile[channel_number] = open( self.get_file_path(channel_number), "wb")

            # write the sound buffer to the file
            self.aOutfile[channel_number].write( aSoundData[channel_number].tobytes() )

            # save the data in the dataframe
            if self.save_csv and not self.stop_csv_save:
                new_df = pd.DataFrame()
                new_df["aTimeStamp"] = [aTimeStamp[0] + aTimeStamp[1] / 1000000.0] * len(aSoundData[channel_number])
                new_df["audio"] = aSoundData[channel_number]
                new_df["frequency"] = self.soundDataFrequency(aSoundData[channel_number])
                new_df["loudness"] = self.soundDataLoudness(aSoundData[channel_number])

                self.dfs[channel_number] = self.dfs[channel_number].append(new_df, ignore_index=True)

        speechDetected = self.speechDetected(aSoundData)

        # check if the loudness is above the threshold
        if speechDetected:
            self.last_sound_above_loudness_threshold = aTimeStamp
            self.at_least_one_sound = True

        # check if the sentence timeout has been reached
        if self.one_sentence and self.at_least_one_sound and self.last_sound_above_loudness_threshold and time_between(self.last_sound_above_loudness_threshold, aTimeStamp) > self.sentence_timeout:
            self.build_wav_files(number_of_channels=1)
            # close everything
            self.stop()
            self.at_least_one_sound = False

        self.count_for_live_wav_save += 1

        if self.live_wav_each == self.count_for_live_wav_save and self.live_wav_each != 0:
            self.count_for_live_wav_save = 0
            self.build_wav_files(number_of_channels=1)


    def get_file_path(self, channel_number, extension=".raw"):
        """return the file path for the given channel number and extension"""
        if extension[0] != ".":
            extension = "." + extension

        dict_dir = {
            ".raw": self.raw_dir,
            ".wav": self.wav_dir,
            ".csv": self.csv_dir
        }

        if extension not in dict_dir.keys():
            raise ValueError("extension must be" + " or ".join(dict_dir.keys()))
        
        if dict_dir[extension][-4:] == extension:
            return dict_dir[extension]

        res = dict_dir[extension] + "out_" + str(channel_number) + "_" + self.date_and_time + extension

        # check if the folder exists
        if not os.path.exists(os.path.dirname(res)):
            os.makedirs(os.path.dirname(res))
        
        return res
    

    def build_wav_files(self, number_of_channels=4):
        """build the wav files from the raw files"""
        for channel_number in range(0, number_of_channels):
            # get both file paths
            raw_file_path = self.get_file_path(channel_number, ".raw")
            wav_file_path = self.get_file_path(channel_number, ".wav")
            build_wav_from_raw(raw_file_path, wav_file_path)
    
    def build_csv_files(self, number_of_channels=4):
        """build the csv files from the dataframes"""
        if not self.save_csv:
            return
        self.stop_csv_save = True
        for channel_number in range(0, number_of_channels):
            self.dfs[channel_number].to_csv(self.get_file_path(channel_number, ".csv"), index=False)



#%% FUNCTIONS ==========================================================================================================

def build_wav_from_raw(raw_file_path, wav_file_path, sample_rate=48000, sample_width=2, n_channels=1):
    """build a .wav file from a .raw file"""

    with open(raw_file_path, 'rb') as raw_file:
        raw_data = raw_file.read()
    
    # check if the folder exists
    if not os.path.exists(os.path.dirname(wav_file_path)):
        os.makedirs(os.path.dirname(wav_file_path))

    wav_file = wave.open(wav_file_path, 'wb')
    wav_file.setnchannels(n_channels)
    wav_file.setsampwidth(sample_width)
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(raw_data)
    
    wav_file.close()


def time_between(timeStamp1, timeStamp2):
    """return the time between the two time stamps"""
    # timeStamp is a list of two integers: [seconds, microseconds]
    return (timeStamp2[0] - timeStamp1[0]) + ( (timeStamp2[1] - timeStamp1[1]) / 1000000.0 )

#%% MAIN ===============================================================================================================

def main():

    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    parser = OptionParser()
    parser.add_option("--pip",
        help="Parent broker port. The IP address or your robot",
        dest="pip")
    parser.add_option("--pport",
        help="Parent broker port. The port NAOqi is listening to",
        dest="pport",
        type="int")
    parser.set_defaults(
        pip=NAO_IP,
        pport=9559)

    (opts, args_) = parser.parse_args()
    pip   = opts.pip
    pport = opts.pport

    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = naoqi.ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       pip,         # parent broker IP
       pport)       # parent broker port


    # Warning: SoundReceiver must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global SoundReceiver
    SoundReceiver = SoundReceiverModule(
        "SoundReceiver",
        pip,
        one_sentence=False,
        sentence_timeout=3,
        save_csv=False
        )
    SoundReceiver.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Interrupted by user, shutting down")
        SoundReceiver.build_wav_files()
        SoundReceiver.build_csv_files()
        myBroker.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()