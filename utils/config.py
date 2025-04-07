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
    def get_source_data():
        try:
            data_path = Config.CONFIG_PARSER.get('data source', 'data_source_path')
        except Exception:
            return ''
        return data_path
    
    
    @staticmethod
    def store_model():
        try:
            model_path = Config.CONFIG_PARSER.get('model', 'model_path')
        except Exception:
            model_path = os.path.join(Config.get_workspace_folder(), 'model')
        os.makedirs(model_path, exist_ok=True)
        return model_path
