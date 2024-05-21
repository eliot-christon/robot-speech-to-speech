import logging
import pandas as pd
import os
from typing import List
from langchain.docstore.document import Document
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings.ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

class RetrieveAndAugment:
    """Class to retrieve and augment the data from the database."""

#%% CONSTRUCTOR ==========================================================================================================

    def __init__(self, 
                 input_database_folder: str, 
                 input_question_text_file: str, 
                 output_text_file: str, 
                 output_csv_file: str,
                 load_directory: str,
                 ollama_model: str,
                 input_additional_files: List[str] = [], 
                 number_of_results: int = 3,
                 chunk_size: int = 1000,):
        """Constructor for the RetrieveAndAugment class."""
        # files
        self.__init_input_files(input_database_folder, input_additional_files)
        self.__input_file = input_question_text_file
        self.__output_text_file = output_text_file
        self.__output_csv_file = output_csv_file
        # IO other attributes
        self.__embeddings = OllamaEmbeddings(model=ollama_model)
        self.__ollama_model = ollama_model.replace(":","")
        self.__number_of_results = number_of_results
        self.__chunk_size = chunk_size
        self.__load_directory = load_directory + f"{self.__ollama_model}"
        self.__vectordb = self.load_vectordb()
        # internal attributes
        self.__running = False
        self.__df = pd.DataFrame(columns=["filename", "page", "chunk", "score"])

        self.start() # the first call could be longer because of the embeddings usage, ollama model loading, etc.

#%% METHODS ==============================================================================================================

    def __init_input_files(self, input_database_folder: str, input_additionnal_files: List[str], supported_extensions: List[str] = ["txt"]):
        """Initialize the input files."""
        self.__input_db_files = [os.path.join(input_database_folder, file) for file in os.listdir(input_database_folder) if file.split(".")[-1] in supported_extensions]
        self.__input_db_files += input_additionnal_files
        print(f"Input files: {self.__input_db_files}")

    def __augment(self, search_results: list) -> str:
        """Augment the search results."""
        separator = f"\n{'-' * 100}\n"
        if len(search_results) == 0:
            return "No results found."
        if isinstance(search_results[0], tuple):
            return separator.join([f"Extrait de document {i+1}: {d.metadata['filename'].split('/')[-1]}\n\n{d.page_content}" for i, (d, _) in enumerate(search_results)])
        else:
            return separator.join([f"Extrait de document {i+1}: {d.metadata['filename'].split('/')[-1]}\n\n{d.page_content}" for i, d in enumerate(search_results)])

    def __text_to_docs(self, text: List[str], filename: str) -> List[Document]:
        if isinstance(text, str):
            text = [text]
        page_docs = [Document(page_content=page) for page in text]
        for i, doc in enumerate(page_docs):
            doc.metadata["page"] = i + 1

        doc_chunks = []
        for doc in page_docs:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.__chunk_size,
                separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
                chunk_overlap=0,
            )
            chunks = text_splitter.split_text(doc.page_content)
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk, metadata={"page": doc.metadata["page"], "chunk": i}
                )
                doc.metadata["source"] = f"{doc.metadata['page']}-{doc.metadata['chunk']}"
                doc.metadata["filename"] = filename  # Add filename to metadata
                doc_chunks.append(doc)
        return doc_chunks

    def __docs_to_index(self, docs):
        index = FAISS.from_documents(docs, embedding=self.__embeddings, normalize_L2=True)
        return index
    
    def load_vectordb(self) -> FAISS:
        # check if the directory exists
        if not os.path.exists(self.__load_directory):
            logging.warning(f"T10_RetrieveAndAugment: The directory {self.__load_directory} does not exist. Updating the vectordb.")
            return self.update_vectordb()
        return FAISS.load_local(self.__load_directory, embeddings=self.__embeddings, allow_dangerous_deserialization=True, normalize_L2=True)

    def update_vectordb(self) -> FAISS:
        docs = []
        for file in self.__input_db_files:
            with open(file, "r") as f:
                text = f.read()
            docs += self.__text_to_docs(text, file)
        vectordb = self.__docs_to_index(docs)
        self.__vectordb = vectordb
        # check if the load directory exists, else create it
        if not os.path.exists(self.__load_directory):
            os.makedirs(self.__load_directory)
        # save the vectordb
        vectordb.save_local(self.__load_directory)
        logging.info("T10_RetrieveAndAugment: Updated the vectordb.")
        return vectordb

#%% GETTERS AND SETTERS ==================================================================================================

    def get_running(self):
        return self.__running

#%% COMMANDS =============================================================================================================

    def start(self):
        self.__running = True

        # read the question
        with open(self.__input_file, "r") as f:
            question = f.read()
        
        # retrieve the most similar documents
        search_results = self.__vectordb.similarity_search_with_score(question, k=self.__number_of_results)
        
        # augment the results
        search_results_str = self.__augment(search_results)

        # build the dataframe
        self.__df = pd.DataFrame(columns=["filename", "page", "chunk", "score"])
        for i, (doc, score) in enumerate(search_results):
            self.__df.loc[i] = [doc.metadata["filename"], doc.metadata["page"], doc.metadata["chunk"], score]
        
        # save the dataframe to the output csv file
        self.__df.to_csv(self.__output_csv_file, index=False)

        # write the results to the output file
        with open(self.__output_text_file, "w") as f:
            f.write(search_results_str)

        self.__running = False
        logging.info("T10_RetrieveAndAugment: Finished.")