import logging

class PersonRecognition:
    """Class for person recognition"""

#%% CONSTRUCTOR ==========================================================================================================

    def __init__(self, output_text_file:str):
        self.__text_file = output_text_file
        self.__running = False

#%% METHODS ==============================================================================================================

    def __write_to_file(self):
        """Write the output text to a file"""
        with open(self.__text_file, 'w', encoding='utf-8') as file:
            file.write("Jean DUPONT")

#%% GETTERS AND SETTERS ==================================================================================================

    def get_running(self) -> bool:
        return self.__running
    
#%% START ================================================================================================================

    def start(self):
        """Start the process"""

        logging.info("PersonRecognition: Starting...")

        self.__running = True

        self.__write_to_file()

        self.__running = False
