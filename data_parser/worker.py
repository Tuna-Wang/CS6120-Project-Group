# -*- coding: utf-8 -*-
import re
import os
import fitz
import json
import nltk
from nltk.corpus import words
from utils.config import Config
from utils.const import InputDataTitles

class Worker:
    def __init__(self, logger):
        self.logger = logger
        self.file_path = Config.get_source_data()
        self.text = ''
        self.data = []

    def extract_data_from_pdf(self):
        self.logger.info('Extracting data from PDF file')
        try:
            self.doc = fitz.open(self.file_path)
        except Exception as e:
            self.logger.error(f'Error while opening file: {e}')
            return False
        
        for page in self.doc:
            self.text += page.get_text()
        self.doc.close()
        # dump it in a txt file
        file_name = os.path.basename(self.file_path).split('.')[0] + '.txt'
        with open(os.path.join(Config.get_workspace_folder(), file_name), 'w') as f:
            f.write(self.text)
        return True


    def parse_data(self):
        self.logger.info('Parsing data')
        self.data = []
        raw_data = self.text.split('\n')
        print(raw_data)
        for index, line in enumerate(raw_data):
            if not line:
                continue
            if line[0].lower() == InputDataTitles.TARGET_CHAR.lower():
                if not self._error_detector(line):
                    self.logger.error(f'Error in line {index}: {line}')
                self.data.append(" ".join(line.split()[1:]))
        file_name = InputDataTitles.TARGET_CHAR + '_script'
        with open(os.path.join(Config.get_workspace_folder(), f"{file_name}.json"), 'w') as f:
            json.dump(self.data, f)
        return self.data
    
    def _error_detector(self, line):
        try:
            english_vocab = set(w.lower() for w in words.words())
        except:
            nltk.download('words')
            english_vocab = set(w.lower() for w in words.words())
        custom_words = {}

        if custom_words:
            valid_words = english_vocab.union(custom_words)
        word_pattern = re.compile(r'\b\w+\b')
        errors = []
      
        token = word_pattern.findall(line)
        for word in token:
            if any(c.isdigit() for c in word):
                continue
            if word[0].isupper() and word[1:].islower():
                continue

            if word.lower() not in valid_words:
                return False
        return True
        