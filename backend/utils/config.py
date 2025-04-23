# -*- coding: utf-8 -*-

import os
from configparser import ConfigParser

from utils.const import CONFIG_FILE


class Config:
    CONFIG_PARSER = ConfigParser()
    CONFIG_PARSER.read(CONFIG_FILE)

    @staticmethod
    def get_workspace_folder():
        try:
            workspace_folder = Config.CONFIG_PARSER.get('common', 'workspace')
        except Exception:
            workspace_folder = 'workspace'
        os.makedirs(workspace_folder, exist_ok=True)
        return workspace_folder

    @staticmethod
    def get_log_folder():
        try:
            log_folder = os.path.join(Config.get_workspace_folder(), Config.CONFIG_PARSER.get('common', 'log_folder'))
        except Exception:
            log_folder = os.path.join(Config.get_workspace_folder(), 'logs')
        os.makedirs(log_folder, exist_ok=True)
        return log_folder
    
    @staticmethod
    def get_api_key():
        try:
            api_key = Config.CONFIG_PARSER.get('common', 'api_key')
        except Exception:
            api_key = ''
        return api_key

    @staticmethod
    def get_source_data_path():
        try:
            data_path = Config.CONFIG_PARSER.get('data_source', 'data_source_path')
        except Exception:
            return ''
        return data_path

    @staticmethod
    def get_personal_data_path():
        try:
            personal_data = Config.CONFIG_PARSER.get('data_source', 'personal_data_path')
        except Exception:
            personal_data = ''
        return personal_data

    @staticmethod
    def get_vector_db_dir():
        try:
            model_path = Config.CONFIG_PARSER.get('rag', 'vector_db_dir')
        except Exception:
            model_path = os.path.join(Config.get_workspace_folder(), 'model')
        os.makedirs(model_path, exist_ok=True)
        return model_path

    @staticmethod
    def personal_rag_enabled():
        try:
            return Config.CONFIG_PARSER.getboolean('imitation', 'personal_rag_enabled')
        except Exception:
            return True
