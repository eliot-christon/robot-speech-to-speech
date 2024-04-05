import logging
import ollama

class ActionSelection:
    """Class for selecting actions from a text file."""

#%% CONSTRUCTOR ==========================================================================================================

    def __init__(self, input_text_file:str, output_text_file:str):
        self.__input_file = input_text_file
        self.__output_file = output_text_file

#%% METHODS ==============================================================================================================
    
#%% GETTERS AND SETTERS ==================================================================================================
    
    def get_running(self) -> bool:
        return self.__running
    
    def get_model_name(self) -> str:
        return self.__model_name
    
    def set_model_name(self, model_name:str):
        self.__model_name = model_name
    
#%% START =================================================================================================================
    
    def start(self):
        """Start the text generation process"""

        self.__running = True

        self.__running = False

        logging.info("ActionSelection: Finished.")
    