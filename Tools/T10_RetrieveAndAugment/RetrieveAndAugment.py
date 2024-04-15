import logging
import os
from typing import List, Tuple
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
                 input_additional_files: List[str] = [], 
                 number_of_results: int = 3):
        """Constructor for the RetrieveAndAugment class."""
        self.__init_input_files(input_database_folder, input_additional_files)
        self.__input_file = input_question_text_file
        self.__output_file = output_text_file
        self.__embeddings = OllamaEmbeddings()
        self.__vectordb, self.__docs = self.__get_index_for_txt(self.__input_db_files)
        self.__number_of_results = number_of_results

        self.__running = False

#%% METHODS ==============================================================================================================

    def __init_input_files(self, input_database_folder: str, input_additionnal_files: List[str], supported_extensions: List[str] = ["txt"]):
        """Initialize the input files."""
        self.__input_db_files = [os.path.join(input_database_folder, file) for file in os.listdir(input_database_folder) if file.split(".")[-1] in supported_extensions]
        self.__input_db_files += input_additionnal_files

    def __augment(self, search_results: list) -> str:
        """Augment the search results."""
        separator = "\n\n" + "="*50 + "\n\n"
        if len(search_results) == 0:
            return "No results found."
        if isinstance(search_results[0], tuple):
            return separator.join([f"proba :{doc[1]}\n\n{doc[0].page_content}" for doc in search_results])
        else:
            return separator.join([doc.page_content for doc in search_results])

    def __text_to_docs(self, text: List[str], filename: str) -> List[Document]:
        if isinstance(text, str):
            text = [text]
        page_docs = [Document(page_content=page) for page in text]
        for i, doc in enumerate(page_docs):
            doc.metadata["page"] = i + 1

        doc_chunks = []
        for doc in page_docs:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
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
        index = FAISS.from_documents(docs, self.__embeddings)
        return index

    def __get_index_for_txt(self, text_files: List[str]) -> Tuple[FAISS, List[Document]]:
        docs = []
        for file in text_files:
            with open(file, "r") as f:
                text = f.read()
            docs += self.__text_to_docs(text, file)
        index = self.__docs_to_index(docs)
        return index, docs

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
        search_results = self.__vectordb._similarity_search_with_relevance_scores(question, k=self.__number_of_results)

        # augment the results
        search_results_str = self.__augment(search_results)

        # write the results to the output file
        with open(self.__output_file, "w") as f:
            f.write(search_results_str)

        self.__running = False
        logging.info("RetrieveAndAugment: Finished.")