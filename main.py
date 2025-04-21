#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
from logging.config import fileConfig

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from langchain.schema import Document

from utils.const import LOG_CONFIG_FILE, Characters
from utils.config import Config
from data_parser.worker import Worker as DataParserWorker
from DB_creator.worker import Worker as DBWorker
from Imitation.general_worker import Worker as ImitationWorker


class APIService:
    def __init__(self):
        # Prepare logging
        config = {'debug_logfile': os.path.join(Config.get_log_folder(), 'main.log')}
        fileConfig(LOG_CONFIG_FILE, config)
        self.logger = logging.getLogger()
        
        # Initialize components
        self.data_parser = DataParserWorker(self.logger)
        self.db_worker = None
        self.imitation_worker = None
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
            self.db_worker.create_all_vector_db(5)
            self.logger.debug("Stylish vector databases created")

            # Initialize imitation worker
            self.imitation_worker = ImitationWorker(self.db_worker, self.logger)

            self.is_initialized = True
            self.logger.info("Pipeline initialized successfully")
        else:
            self.logger.info("Already initialized")


# Global service instance
api_service = APIService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern replacement for @app.on_event("startup/shutdown")"""
    # Initialize pipeline on startup
    config = {'debug_logfile': os.path.join(Config.get_log_folder(), 'main.log')}
    fileConfig(LOG_CONFIG_FILE, config)
    
    #print("Initializing pipeline...")
    #global api_service
    #api_service.initialize_pipeline()
    #print("Pipeline initialized")

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


class Request(BaseModel):
    text: str
    character: str = Characters.CHARACTER_H


@app.get("/")
async def root():
    return {"status": "ok"}

def custom_decoder(obj):
        if isinstance(obj, Document):
            return {
                "page_content": obj.page_content,
                "metadata": obj.metadata
            }
        return obj

@app.post("/api/imitate")
async def imitate_style(request: Request):
    try:
        if not api_service.is_initialized:
            api_service.initialize_pipeline()

        response = api_service.imitation_worker.imitate(request.text, request.character)
        return {"status": "success", "response": json.dumps(response, default=custom_decoder)}
    except Exception as e:
        api_service.logger.exception(f"Error in imitation: {str(e)}")
        return {"error": str(e), "status": "error"}



if __name__ == '__main__':
    import uvicorn
    # Run both the initialization and the API server
    api_service.initialize_pipeline()
    
    response = api_service.imitation_worker.imitate("What should I do on Monday?", 
                                                    Characters.CHARACTER_H
                                                    )
    print("Response from imitation:", response)
    print(json.dumps(response, default=custom_decoder, indent=2))
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
