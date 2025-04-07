import pandas as pd
from utils.const import InputDataTitles
from utils.config import Config
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS 

# !!! more config needed for switching gpu/cpu
class Worker:
    def __init__(self, logger, df):
        self.logger = logger
        self.df = df
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})
      
    def create_vector_db(self):
        # Filter out the lines from the target speaker
        filter= self.df['speaker'].apply(lambda x: x == InputDataTitles.TARGET_CHAR)
     
        # use target_lies to filter the df
        target_lines = self.df[filter]['text'].tolist()
    
        vector_db = FAISS.from_texts(target_lines, self.embbeddings)
        vector_db.save_local(Config.store_model())
        return vector_db

    def get_retriever(self, vector_db = None):
        if vector_db is None:
            vector_db = FAISS.load_local(Config.store_model(), self.embeddings)
        retriever = vector_db.as_retriever(search_kwargs={"k": 5})
        return retriever

