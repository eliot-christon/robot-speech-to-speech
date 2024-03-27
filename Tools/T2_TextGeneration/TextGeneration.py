import logging
import ollama

class TextGeneration:
    """Class for generating text from a pre-trained text model."""

#%% CONSTRUCTOR ==========================================================================================================

    def __init__(self, input_text_file:str, output_text_file:str, model_name:str, ollama_generate_options:dict):
        self.__input_file = input_text_file
        self.__output_file = output_text_file
        self.__model_name = model_name
        self.__options = ollama_generate_options

        self.__running = False
        self.__text = ""

        # Initialize the Ollama model with the given model name by generating from nearly empty prompt
        ollama.generate(
            model=self.__model_name,
            prompt=" ",
            stream=False,
            options=self.__options
        )

#%% METHODS ==============================================================================================================
    
    def __write_to_file(self):
        """Write the generated text to the output text file."""
        with open(self.__output_file, "w", encoding='utf-8') as file:
            file.write(self.__text)
    
    def __read_from_file(self):
        """Read the input text from the input text file."""
        with open(self.__input_file, "r", encoding='utf-8') as file:
            return file.read()

#%% GETTERS AND SETTERS ==================================================================================================
    
    def get_running(self) -> bool:
        return self.__running
    
    def get_text(self) -> str:
        return self.__text
    
    def get_model_name(self) -> str:
        return self.__model_name
    
    def set_model_name(self, model_name:str):
        self.__model_name = model_name
    
#%% START =================================================================================================================
    
    def start(self):
        """Start the text generation process"""

        self.__running = True
        self.__text = ""

        try:
            stream = ollama.generate(
                model=self.__model_name,
                prompt=self.__read_from_file(),
                stream=True,
                options=self.__options
            )
            for chunk in stream:
                self.__text += chunk['response']
                self.__write_to_file()
            
        except Exception as e:
            logging.error(f"TextGeneration: Error while generating text: {e}")
        
        # Add a dot at the end of the text
        self.__text += "."
        self.__write_to_file()

        self.__running = False

        logging.info("TextGeneration: Finished.")
    