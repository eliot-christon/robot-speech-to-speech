import logging
import requests

class RightsManagement:
    """Class to control the RightsManagement through an ODM server"""

#%% CONSTRUCTOR ==========================================================================================================

    def __init__(self, input_url_api_request:str, input_person_reconized_file:str, input_people_folder:str, output_documents_autorized_file:str, output_actions_autorized_file:str):
        self.__input_url_api_request           = input_url_api_request
        self.__input_person_reconized_file     = input_person_reconized_file
        self.__input_people_folder             = input_people_folder
        self.__output_documents_autorized_file = output_documents_autorized_file
        self.__output_actions_autorized_file   = output_actions_autorized_file
        self.__running = False

#%% METHODS ==============================================================================================================

    def __read_person_reconized(self) -> str:
        """Read the person reconized"""
        with open(self.__input_person_reconized_file, "r") as file:
            res = file.read().strip()
        if res == "":
            return "Unknown"
        return res
    
    def __get_level_of_duty(self, person:str) -> str:
        """Get the level of duty of a person reading the people folder / person folder / level_of_duty.txt"""
        with open(f"{self.__input_people_folder}/{person}/level_of_duty.txt", "r") as file:
            return file.read().strip()
    
    def __api_request(self, person:str, level_of_duty:str) -> requests.Response:
        """Make an API request to the RightsManagement API"""
        url = f"{self.__input_url_api_request}?person={person}&level_of_duty={level_of_duty}" # TODO: Check if the URL is correct
        response = requests.post(url)
        return response

    def __write_autorized_documents(self, autorisations:dict):
        """Write the autorized documents in the output file"""
        with open(self.__output_documents_autorized_file, "w", encoding="utf-8") as file:
            for document in autorisations["documents"]:
                file.write(f"{document}\n")

    def __write_autorized_actions(self, autorisations:dict):
        """Write the autorized actions in the output file"""
        with open(self.__output_actions_autorized_file, "w", encoding="utf-8") as file:
            for action in autorisations["actions"]:
                file.write(f"{action}\n")
    
#%% GETTERS AND SETTERS ==================================================================================================

    def get_running(self):
        return self.__running

#%% COMMANDS =============================================================================================================
    def start(self):
        self.__running = True

        person        = self.__read_person_reconized()
        level_of_duty = self.__get_level_of_duty(person)
        try :
            response      = self.__api_request(person, level_of_duty)
            try :
                autorisations = response.json()["autorisations"]
            except Exception as e:
                logging.error(f"T12_RightsManagement: Error during the JSON parsing: {e}")
                self.__running = False
                return
        except Exception as e:
            logging.error(f"T12_RightsManagement: Error during the API request: {e}")
            self.__running = False
            autorisations = {"documents": [], "actions": ["Se réidentifier", "Dire au revoir"]}
        
        self.__write_autorized_documents(autorisations)
        self.__write_autorized_actions(autorisations)

        self.__running = False
        logging.info("T12_RightsManagement: Finished.")
