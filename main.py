#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from logging.config import fileConfig

from utils.const import LOG_CONFIG_FILE, InputDataTitles
from utils.config import Config
from data_parser.worker import Worker as DataParserWorker
from DB_creator.worker import Worker as DBWorker
from Imitation.personal_worker import Worker as ImitationWorker
from Imitation.general_worker import Worker as ImitationWorkerCustomized


class APIService:
    def __init__(self):

        # Prepare logging
        self.logger = logging.getLogger()
        
        # Initialize components
        self.data_parser = DataParserWorker(self.logger)
        self.db_worker = None
        self.imitation_worker_general = None
        self.imitation_worker_personal = None
        self.character_retriever = None
        self.personal_retriever = None
        self.is_initialized = False



    def initialize_pipeline(self):
        """Initialize the full pipeline if not already done"""
        if not self.is_initialized:
            self.logger.info("Initializing pipeline...")
            
            # Extract data from PDF
            df = self.data_parser.parse_data()
            self.logger.debug(f"DataFrame shape: {df.shape}")

            # Create character vector database
            self.db_worker = DBWorker(self.logger, df)
            v_path = Config.store_model()
            if not os.path.exists(v_path) or not os.listdir(v_path):
                self.db_worker.create_vector_db()
            self.logger.debug("Character Vector database created")

            
            # Create personal vector database
            # If there is no personal data or the data is not valid, then no retriever will be created
            # We will only use one retriever which is the character retriever
            if self.db_worker.create_personal_vector_db():
                self.personal_retriever = self.db_worker.get_personal_retriever()
            else:
                self.logger.error("Failed to create personal vector database")
                    

            # Get general/character retriever
            self.character_retriever = self.db_worker.get_character_retriever()
            
            
            # Initialize imitation worker
            self.imitation_worker_general = ImitationWorker(
                self.logger
            )

            # If the personal retriver is not None, then we can use the customized imitation worker
            if self.personal_retriever:
                self.imitation_worker_personal = ImitationWorkerCustomized(
                    self.logger
                )
            
            self.is_initialized = True
            self.logger.info("Pipeline initialized successfully")

# Global service instance
api_service = APIService()


class Request(BaseModel):
    text: str
    character: str = InputDataTitles.DEFAULT_CHARACTER
    api_key: str 


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern replacement for @app.on_event("startup/shutdown")"""
    # Initialize pipeline on startup
    config = {'debug_logfile': os.path.join(Config.get_log_folder(), 'main.log')}
    fileConfig(LOG_CONFIG_FILE, config)
    
    print("Initializing pipeline...")
    global api_service
    api_service.initialize_pipeline()
    print("Pipeline initialized")


    
    yield  
    

# Initialize the FastAPI app
app = FastAPI(title="Style Imitation API", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/api/imitate")
async def imitate_style(request: Request):
    """
    Endpoint for style imitation
    Args:
        text: Input text to process
        character: Character to imitate (defaults to TARGET_CHAR)
    """
    try:
        if not api_service.is_initialized:
            api_service.initialize_pipeline()
        

        if not api_service.personal_retriever:
            response = api_service.imitation_worker_general.imitate(
                api_service.character_retriever,
                request.text,
                character=request.character,
                api_key=request.api_key
            )
            return {"response": response, "status": "success"}
        else:
            response = api_service.imitation_worker_personal.imitate(
                request.text,
                api_service.character_retriever,
                api_service.personal_retriever,
                character=request.character,
                api_key=request.api_key
            )
            return {"response": response, "status": "success"}
        



    except Exception as e:
        api_service.logger.error(f"Error in imitation: {str(e)}")
        return {"error": str(e), "status": "error"}

if __name__ == '__main__':
    import uvicorn
    # Run both the initialization and the API server
    api_service.initialize_pipeline()
    uvicorn.run(app, host="0.0.0.0", port=8000)
