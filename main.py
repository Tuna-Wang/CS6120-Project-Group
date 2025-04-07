#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging

from logging.config import fileConfig

from utils.const import LOG_CONFIG_FILE
from utils.config import Config
from utils.const import InputDataTitles

from data_parser.worker import Worker as DataParserWorker
from DB_creator.worker import Worker as DBWorker
if __name__ == '__main__':
     # Prepare logging
    config = {'debug_logfile': os.path.join(Config.get_log_folder(), 'main.log')}
    fileConfig(LOG_CONFIG_FILE, config)
    logger = logging.getLogger()

    # Extract data from PDF
    data_parser = DataParserWorker(logger)
    df = data_parser.parse_data()

    # Create vector database
    db_worker = DBWorker(logger, df)
    db_worker.create_vector_db()
