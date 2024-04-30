import logging
import ollama
import joblib
import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.ensemble import RandomForestClassifier
import os

class ActionSelection:
    """Class for selecting actions from a text file."""

#%% CONSTRUCTOR ==========================================================================================================

    def __init__(self, input_text_file:str, output_text_file:str, pretrained_model_folder:str, model_name:str, action_selection_dataset_path:str):
        self.__input_file = input_text_file
        self.__output_file = output_text_file
        self.__pretrained_model_folder = pretrained_model_folder
        self.__model_name = model_name
        self.__action_selection_dataset = pd.read_csv(action_selection_dataset_path)

        self.__running = False
        self.__embedding_len = len(self.__vectorize("test"))
        self.__get_classifier()
        self.__feature_names = np.array([f"vector_{i}" for i in range(self.__embedding_len)])

#%% METHODS ==============================================================================================================
    
    def __load_text(self) -> str:
        """Load the text from the input file"""
        with open(self.__input_file, "r") as file:
            text = file.read()
        return text
    
    def __save_text(self, text:str):
        """Save the text to the output file"""
        with open(self.__output_file, encoding="utf-8", mode="w") as file:
            file.write(text)
    
    def __vectorize(self, text:str) -> np.ndarray:
        return np.array(ollama.embeddings(model=self.__model_name, prompt=text)['embedding'])
    
    def __get_classifier(self):
        """Get the classifier"""
        if os.path.exists(self.__pretrained_model_folder + self.__model_name + "_classifier.joblib"):
            self.__classifier = joblib.load(self.__pretrained_model_folder + self.__model_name + "_classifier.joblib")
        else:
            logging.warning("ActionSelection: Classifier not found. Training a new classifier.")
            self.__train_classifier()
    
    def __save_classifier(self):
        """Save the classifier"""
        joblib.dump(self.__classifier, self.__pretrained_model_folder + self.__model_name + "_classifier.joblib")

    def __train_classifier(self):
        """Train the classifier"""
        # for each sentence in the df, get the vector
        vect_columns = [f"vector_{i}" for i in range(self.__embedding_len)]

        vector_action_df = pd.DataFrame()

        for sentence in tqdm(self.__action_selection_dataset["assistant_sentence"]):
            vector = self.__vectorize(sentence)
            if len(vector_action_df) == 0:
                vector_action_df = pd.DataFrame([vector], columns=vect_columns)
            else:
                vector_action_df = pd.concat([vector_action_df, pd.DataFrame([vector], columns=vect_columns)], ignore_index=True)

        # add the assistant_sentence and action columns
        vector_action_df["assistant_sentence"] = self.__action_selection_dataset["assistant_sentence"]
        vector_action_df["action"] = self.__action_selection_dataset["action"]
        # replace null values with "Unknown"
        vector_action_df["action"] = vector_action_df["action"].fillna("Unknown")
        # place the assistant_sentence and action columns at the beginning
        cols = vector_action_df.columns.tolist()
        cols = cols[-2:] + cols[:-2]
        vector_action_df = vector_action_df[cols]

        # train the classifier
        y = vector_action_df["action"]
        X = vector_action_df.drop(columns=["assistant_sentence", "action"])

        sample_weights = y.value_counts(normalize=True).to_dict()

        self.__classifier = RandomForestClassifier(class_weight=sample_weights, random_state=42)
        self.__classifier.fit(X, y)

        self.__save_classifier()
    
#%% GETTERS AND SETTERS ==================================================================================================
    
    def get_running(self) -> bool:
        return self.__running
    
    def get_model_name(self) -> str:
        return self.__model_name
    
    def set_model_name(self, model_name:str):
        self.__model_name = model_name
        
    def get_input_file(self) -> str:
        return self.__input_file
    
#%% START =================================================================================================================
    
    def start(self):
        """Start the text generation process"""

        self.__running = True

        text = self.__load_text()
        vector = self.__vectorize(text)
        vector = pd.DataFrame(vector.reshape(1, -1), columns=self.__feature_names)
        action_result = self.__classifier.predict(vector).item()
        self.__save_text(action_result)

        self.__running = False

        logging.info("ActionSelection: Finished.")
    