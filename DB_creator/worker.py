
import os
from utils.const import InputDataTitles
from utils.config import Config
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS 

# !!! more config needed for switching gpu/cpu
class Worker:
    def __init__(self, logger, df):
        self.logger = logger
        self.df = df
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})
      
    def create_vector_db(self):
        """Create separate vector DBs for each character"""
        for character in InputDataTitles.CHAR_SET:
            print(f"Creating vector DB for character: {character}")
            try:
                # Filter and validate data
                character_lines = self.df[self.df['speaker'] == character]['text'].tolist()
                if not character_lines:
                    self.logger.warning(f"No lines found for character: {character}")
                    continue
                
                # Create and save vector DB
                vector_db = FAISS.from_texts(
                    character_lines, 
                    self.embeddings
                )
                save_path = os.path.join(Config.store_model(), f"{character}_vector_db")
                vector_db.save_local(save_path)
                print(f"Vector DB for {character} saved at: {save_path}")
                self.logger.info(f"Created vector DB for {character} at {save_path}")
                
            except Exception as e:
                self.logger.error(f"Failed to create vector DB for {character}: {str(e)}")
        
        self.logger.info("Character vector DB creation complete.")
        return True
    
    # Config this to accept file upload
    def create_personal_vector_db(self):
        """Create vector DB from uploaded personal data"""
        personal_data_path = Config.get_personal_data()

        try:
            with open(personal_data_path, 'rb') as f:
                file_content = f.read()
            if not file_content:
                raise ValueError("File is empty or not valid")
            
        except Exception as e:
            self.logger.error(f"Failed to read personal data file: {str(e)}")
            return False

        try:
            if len(file_content) < 100:  # Minimum file size check
                raise ValueError("Invalid file content")
            
            # Load and process
            loader = PyPDFLoader(personal_data_path)
            docs = loader.load()
            
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", "。", "！", "？", "．", ""]
            )
            chunks = splitter.split_documents(docs)
            
            # Create and save vector DB
            personal_db = FAISS.from_documents(chunks, self.embeddings)
            save_path = os.path.join(Config.store_model(), "personal_vector_db")
            personal_db.save_local(save_path)
            return True
            
        except Exception as e:
            self.logger.error(f"Personal DB creation failed: {str(e)}")
            return False

                

    def get_character_retriever(self, character = None, vector_db = None):
        if character is None:
            character = InputDataTitles.DEFAULT_CHARACTER
        if vector_db is None:
            vector_db = FAISS.load_local(
                os.path.join(Config.store_model(), f"{character}_vector_db"), 
                self.embeddings, allow_dangerous_deserialization=True
                )
        # Set the retriever to return the top 3 most relevant documents
        retriever = vector_db.as_retriever(search_kwargs={"k": 3})
        self.logger.info(f"Retriever created for character: {character}")
        return retriever

    def get_personal_retriever(self, vector_db = None):
        if vector_db is None:
            vector_db = FAISS.load_local(os.path.join(Config.store_model(), "personal_vector_db"), self.embeddings, allow_dangerous_deserialization=True)
        # Set the retriever to return the top 3 most relevant documents
        retriever = vector_db.as_retriever(search_kwargs={"k": 3})
        self.logger.info(f"Retriever created for personal data")
        return retriever

          