import os
import logging
from speechbrain.inference.speaker import SpeakerRecognition

class PersonRecognition:
    """Class for person recognition"""

#%% CONSTRUCTOR ==========================================================================================================

    def __init__(self, output_text_file:str, input_audio_file:str, input_people_folder:str, input_model_dir:str):
        self.__text_file = output_text_file
        self.__audio_file = input_audio_file
        self.__people_folder = input_people_folder

        self.__model = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir=input_model_dir + "spkrec-ecapa-voxceleb")

        self.__person_recognized = None
        self.__running = False

#%% METHODS ==============================================================================================================

    def __write_to_file(self):
        """Write the output text to a file"""
        with open(self.__text_file, 'w', encoding='utf-8') as file:
            file.write(self.__person_recognized)
    
    def __list_wav_files(self, folder:str):
        """List all wav files in a folder"""
        files = os.listdir(folder)
        return [f for f in files if f.endswith('.wav')]
    
    def __verify_person(self, person_voices_folder:str):
        """Verify if the audio file is from the person"""
        result = self.__model.verify_files(self.__audio_file, self.__list_wav_files(person_voices_folder)[0])
        return result


#%% GETTERS AND SETTERS ==================================================================================================

    def get_running(self) -> bool:
        return self.__running
    
#%% START ================================================================================================================

    def start(self):
        """Start the process"""

        self.__running = True

        # get all the people in the folder
        people = os.listdir(self.__people_folder)
        people = [person_name for person_name in people if os.path.isdir(self.__people_folder + person_name)]

        # iterate over all the people
        for person_name in people:
            result = self.__verify_person(self.__people_folder + person_name + "/")
            if result:
                self.__person_recognized = person_name
                break
        
        if self.__person_recognized is None:
            self.__person_recognized = "Unknown"
        
        self.__write_to_file()

        self.__running = False

        logging.info("PersonRecognition: Finished.")
