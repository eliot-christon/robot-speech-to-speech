import logging
import ollama
import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import os
import tensorflow as tf
import joblib

class ActionSelection:
    """Class for selecting actions from a text file."""

#%% CONSTRUCTOR ==========================================================================================================

    def __init__(self, input_text_file:str, output_text_file:str, pretrained_model_folder:str, model_name:str, action_selection_dataset_path:str):
        self.__input_file               = input_text_file
        self.__output_file              = output_text_file
        self.__pretrained_model_folder  = pretrained_model_folder
        self.__ollama_model_name        = model_name
        self.__action_selection_dataset = pd.read_csv(action_selection_dataset_path)

        self.__check_make_dir(self.__pretrained_model_folder + self.__ollama_model_name + "/")
        
        self.__classes              = self.__action_selection_dataset["action"].unique()
        self.__num_classes          = len(self.__classes)
        self.__num_features         = self.__pca_N_components + (self.__num_classes * 2) + 1 # pca + sentence similarity (1 / action) + word in action + affirmative flag
        self.__stop_words           = self.__load_stop_words()
        self.__action_embeddings    = self.__get_action_embeddings()
        self.__sentence_embeddings  = self.__get_sentence_embeddings()
        self.__pca_N_components     = 50
        self.__pca                  = self.__get_pca()
        self.__scaler               = StandardScaler()
        self.__clf_epochs           = 300
        self.__clf_train_hist       = None
        self.__classifier           = None

        self.__running = False
#%% METHODS ==============================================================================================================

# LOAD AND SAVE ----------------------------------------------------------------------------------------------------------

    def __load_text(self) -> str:
        """Load the text from the input file"""
        with open(self.__input_file, "r") as file:
            text = file.read()
        return text
    
    def __load_stop_words(self) -> list:
        """Load the stop words"""
        try:
            with open("Tools/T4_ActionSelection/stop_words.txt", "r") as file:
                stop_words = file.readlines()
        except:
            logging.error("T4_ActionSelection: Error loading stop words.")
            stop_words = []
        return stop_words
    
    def __save_text(self, text:str):
        """Save the text to the output file"""
        with open(self.__output_file, encoding="utf-8", mode="w") as file:
            file.write(text)
    
    def __save_classifier(self):
        """Save the classifier"""
        self.__classifier.save(self.__pretrained_model_folder + self.__ollama_model_name + "/classifier.h5")

    def __save_pca(self):
        """Save the PCA"""
        joblib.dump(self.__pca, self.__pretrained_model_folder + self.__ollama_model_name + "/pca.joblib")
    
    def __save_embeddings(self, embeddings:np.ndarray, file_name:str):
        """Save the embeddings"""
        try:
            with open(self.__pretrained_model_folder + self.__ollama_model_name + "/" + file_name, "wb") as file:
                np.save(file, embeddings)
        except:
            logging.error("T4_ActionSelection: Error saving embeddings.")

    def __get_classifier(self):
        """Get the classifier"""
        if os.path.exists(self.__pretrained_model_folder + self.__ollama_model_name + "/classifier.h5"):
            self.__classifier = tf.keras.models.load_model(self.__pretrained_model_folder + self.__ollama_model_name + "/classifier.h5")
        else:
            logging.warning("T4_ActionSelection: Classifier not found. Training a new classifier.")

            self.__classifier = tf.keras.Sequential([
                tf.keras.layers.Dense(32, activation='relu', input_shape=(self.__num_features,)),
                tf.keras.layers.Dense(16, activation='relu'),
                tf.keras.layers.Dense(self.__num_classes, activation='softmax')
            ])

            self.__classifier.compile(optimizer=tf.keras.optimizers.Adam(0.001),
                                      loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                                      metrics=['accuracy'])

            self.__train_classifier()

    def __get_action_embeddings(self):
        """Get the action embeddings"""
        if os.path.exists(self.__pretrained_model_folder + self.__ollama_model_name + "/action_embeddings.npy"):
            self.__action_embeddings = np.load(self.__pretrained_model_folder + self.__ollama_model_name + "/action_embeddings.npy")
        else:
            logging.warning("T4_ActionSelection: Action embeddings not found. New embeddings will be generated.")
            self.__action_embeddings = np.array([self.__vectorize(action) for action in self.__action_selection_dataset["action"]])
            self.__save_embeddings(self.__action_embeddings, "action_embeddings.npy")
    
    def __get_sentence_embeddings(self):
        """Get the sentence embeddings"""
        if os.path.exists(self.__pretrained_model_folder + self.__ollama_model_name + "/sentence_embeddings.npy"):
            self.__sentence_embeddings = np.load(self.__pretrained_model_folder + self.__ollama_model_name + "/sentence_embeddings.npy")
        else:
            logging.warning("T4_ActionSelection: Sentence embeddings not found. New embeddings will be generated.")
            self.__sentence_embeddings = np.array([self.__vectorize(sentence) for sentence in self.__action_selection_dataset["assistant_sentence"]])
            self.__save_embeddings(self.__sentence_embeddings, "sentence_embeddings.npy")

    def __get_pca(self):
        """Get the PCA"""
        if os.path.exists(self.__pretrained_model_folder + self.__ollama_model_name + "/pca.joblib"):
            self.__pca = joblib.load(self.__pretrained_model_folder + self.__ollama_model_name + "/pca.joblib")
        else:
            logging.warning("T4_ActionSelection: PCA not found. New PCA will be generated.")
            self.__pca = PCA(n_components=self.__pca_N_components)
            self.__pca.fit(self.__sentence_embeddings)
            self.__save_pca()

# UTILS ------------------------------------------------------------------------------------------------------------------

    def __check_make_dir(self, path:str):
        """Check if a directory exists, if not, create it"""
        if not os.path.exists(path):
            os.makedirs(path)

    def __cosine_similarity(self, a:np.ndarray, b:np.ndarray) -> float:
        """Get the cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def __vectorize(self, text:str) -> np.ndarray:
        return np.array(ollama.embeddings(model=self.__ollama_model_name, prompt=text)['embedding'])
    
    def __words(self, text:str) -> list:
        chars_to_replace_with_space = ['?', '!', '.', ',', ';', "'", '"']
        words = text.lower()
        for char in chars_to_replace_with_space:
            words = words.replace(char, ' ')
        vocabulary = set()
        for word in words.split():
            if word not in self.__stop_words:
                vocabulary.add(word)
        return list(vocabulary)
    
    def __features(self, text:str, sentence_embeddings:np.ndarray=None) -> np.ndarray:
        """Get the features of the text"""
        if sentence_embeddings is None:
            sentence_embeddings = self.__vectorize(text)
        pca_embeddings      = self.__pca.transform(sentence_embeddings.reshape(1, -1))
        sentence_similarity = np.array([self.__cosine_similarity(sentence_embeddings, self.__vectorize(action)) for action in self.__action_selection_dataset["assistant_sentence"]])
        word_in_action      = np.array([[np.any([word in action for word in self.__words(text)])] for action in self.__classes]).astype(float)
        affirmative_flag    = np.array([0 if text[-1] == '?' else 1]).astype(float)
        res = np.concatenate((pca_embeddings, sentence_similarity, word_in_action, affirmative_flag), axis=1)
        return self.__scaler.transform(res)

    def __train_classifier(self):
        """Train the classifier"""
        X = [self.__features(sentence, self.__sentence_embeddings[i]) for i, sentence in enumerate(self.__action_selection_dataset["assistant_sentence"])]
        y_str = self.__action_selection_dataset["action"]
        y = np.array([np.where(self.__classes == action)[0][0] for action in y_str])

        self.__clf_train_hist = self.__classifier.fit(X, y, epochs=self.__clf_epochs, validation_split=0.1, verbose=0)
        
        self.__save_classifier()
    
#%% GETTERS AND SETTERS ==================================================================================================
    
    def get_running(self) -> bool:
        return self.__running
    
    def get_model_name(self) -> str:
        return self.__ollama_model_name
        
    def get_input_file(self) -> str:
        return self.__input_file
    
    @property
    def clf_train_history(self):
        return self.__clf_train_hist
    
    def set_model_name(self, model_name:str):
        self.__ollama_model_name = model_name
    
#%% START =================================================================================================================
    
    def start(self):
        """Start the text generation process"""

        self.__running = True

        text = self.__load_text()
        features = self.__features(text)
        y_proba = self.__classifier.predict(features)
        action_result = self.__classes[np.argmax(y_proba)]
        self.__save_text(action_result)

        self.__running = False

        logging.info("T4_ActionSelection: Finished.")
    