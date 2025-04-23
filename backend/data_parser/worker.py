# -*- coding: utf-8 -*-
import os
import csv
import pandas as pd
from utils.config import Config
from utils.const import SUPPORTED_CHARACTERS


class Worker:
    def __init__(self, logger):
        self.logger = logger
        self.output_path = os.path.join(Config.get_workspace_folder(), 'parsed_data.csv')

    def parse_data(self):
        """
        This function takes in the text file, and line by line, parse it into a dataframe, and produce also a csv file.
        """
        if not os.path.exists(self.output_path):
            with open (self.output_path, 'w', encoding='utf-8') as out_file:
                out_file = csv.writer(out_file)
                out_file.writerow(['order_index', 'speaker', 'text'])
                order_index = 0  # this is to know if two lines are a conversation pair, or are possibly related to each other.
                with open(Config.get_source_data_path(), 'r', encoding='utf-8') as in_file:
                    for line in in_file:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            line_split = line.split(' ')
                            speaker, text = line_split[0], line_split[1:]
                            if speaker is None or text is None:
                                continue
                            if speaker in SUPPORTED_CHARACTERS and (text[0][0].isupper() or text[0][0] == '(' or text[0][0] == '"' or text[0][0] == "'"):
                                text = ' '.join(text)
                                out_file.writerow([order_index, speaker, text])
                                order_index += 1
                        except Exception as e:
                            self.logger.error(f"Error parsing line: {line}, text: {text}. Error: {e}")
                            continue
            self.logger.info(f"Data parsed successfully and saved to {self.output_path}")
            self.logger.info("Total %d lines parsed", order_index)
        df = pd.read_csv(self.output_path)
        df = df.set_index('order_index')
        df = df.dropna()
        return df
