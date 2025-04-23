import os
from utils.const import SUPPORTED_CHARACTERS
from utils.config import Config
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

MINIMUM_PERSONAL_DATA_SIZE = 100


# !!! more config needed for switching gpu/cpu
class Worker:
    def __init__(self, logger, df, model_name="sentence-transformers/all-MiniLM-L6-v2", device="cpu"):
        self.logger = logger
        self.df = df
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={"device": device})
        self.character_retrievers = {}
        self.context_retrievers = {}
        self.personal_retriever = None

    def create_vector_db(self, text, vdb_name: str, metadata=None):
        vdb_path = os.path.join(Config.get_vector_db_dir(), vdb_name)
        if not text:
            return None
        try:
            # Create and save vector DB
            if metadata:
                vector_db = FAISS.from_texts(text, self.embeddings, metadatas=metadata)
            else:
                vector_db = FAISS.from_texts(text, self.embeddings)
            vector_db.save_local(vdb_path)
            return vector_db
        except Exception as e:
            self.logger.error(f"Failed to create vector DB: {vdb_name}: {str(e)}")
            return None

    def _load_existing_vector_db(self, character: str):
        character_vdb_path = os.path.join(Config.get_vector_db_dir(), f'{character}_vector_db')
        context_vdb_path = os.path.join(Config.get_vector_db_dir(), f'{character}_context_vector_db')
        character_vector_db, context_vbd_path = None, None
        if os.path.exists(character_vdb_path):
            try:
                character_vector_db = FAISS.load_local(character_vdb_path, self.embeddings,
                                                        allow_dangerous_deserialization=True)
            except Exception as e:
                self.logger.warning(f"Could not load existing character vector DB {character}: {str(e)}; create one if possible")
        if os.path.exists(context_vdb_path):
            try:
                context_vector_db = FAISS.load_local(context_vdb_path, self.embeddings,
                                                     allow_dangerous_deserialization=True)
            except Exception as e:
                self.logger.warning(f"Could not load existing context vector DB {character}: {str(e)}; create one if possible")
        return character_vector_db, context_vbd_path


    def create_vector_db_for_character(self, character):
        self.logger.info(f"Creating vector DB for character: {character}")
        character_vector_db, context_vector_db = self._load_existing_vector_db(character)
        
        if not character_vector_db:
            character_df = self.df[self.df['speaker'] == character]
            character_lines = character_df['text'].tolist()
            line_indices = [{'index': i} for i in character_df.index.tolist()]
            if not character_lines:
                self.logger.warning(f"No lines found for character: {character}")
            else:
                character_vector_db = self.create_vector_db(character_lines, f'{character}_vector_db', 
                                                            metadata=line_indices)
        if not context_vector_db:
            context_df = self.df[self.df['speaker'] != character]
            context_lines = context_df['text'].tolist()
            line_indices = [{'index': i} for i in context_df.index.tolist()]
            if not context_lines:
                self.logger.warning(f"No context lines found for character: {character}")
            else:
                context_vector_db = self.create_vector_db(context_lines, f'{character}_context_vector_db',
                                                          metadata=line_indices)
        return character_vector_db, context_vector_db

    # Config this to accept file upload
    def create_personal_vector_db(self):
        """Create vector DB from uploaded personal data"""
        personal_vdb_path = os.path.join(Config.get_vector_db_dir(), 'personal_vector_db')
        if os.path.exists(personal_vdb_path):
            try:
                # Try to load existing vector database
                personal_vector_db = FAISS.load_local(personal_vdb_path,
                                                      self.embeddings,
                                                      allow_dangerous_deserialization=True)
                if personal_vector_db:
                    return personal_vector_db
            except Exception as e:
                self.logger.warning(f"Could not load existing personal vector DB: {str(e)}; create one if possible")            
    
        personal_data_path = Config.get_personal_data_path()
        if not os.path.exists(personal_data_path):
            self.logger.error(f"Personal data file does not exist")
            return None
        if os.stat(personal_data_path).st_size < MINIMUM_PERSONAL_DATA_SIZE:
            self.logger.error("Personal data file is empty or too small")
            return None
    

        try:
            # Load and process
            loader = PyPDFLoader(personal_data_path)
            docs = loader.load()

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", "。", "！", "？", "．", ""]
            )
            chunks = splitter.split_documents(docs)
            chunk_texts = [chunk.page_content for chunk in chunks]
            metadata_list = [{"index": i} for i, chunk in enumerate(chunks)]
            personal_vector_db = self.create_vector_db(chunk_texts, 'personal_vector_db', metadata_list)
            if not personal_vector_db:
                self.logger.error("Failed to create personal vector DB")
                return None
            return personal_vector_db
        except Exception as e:
            self.logger.error(f"Personal DB creation failed: {str(e)}")

        return None

    def create_all_vector_db(self, k=3):
        """Create separate vector DBs for each character"""
        for character in SUPPORTED_CHARACTERS:
            character_vector_db, context_vector_db = self.create_vector_db_for_character(character)
            if character_vector_db:
                self.logger.info(f"Vector DB created for character: {character}")
                self.character_retrievers[character] = character_vector_db.as_retriever(search_kwargs={"k": k})
            if context_vector_db:
                self.logger.info(f"Context vector DB created for character: {character}")
                self.context_retrievers[character] = context_vector_db.as_retriever(search_kwargs={"k": k})
        if Config.personal_rag_enabled():
            personal_vector_db = self.create_personal_vector_db()
            if personal_vector_db:
                self.logger.info("Personal vector DB created")
                self.personal_retriever = personal_vector_db.as_retriever(search_kwargs={"k": k})

    def get_character_retriever(self, character):
        return self.character_retrievers.get(character)

    def get_context_retriever(self, character):
        return self.context_retrievers.get(character)

    def get_personal_retriever(self):
        return self.personal_retriever
