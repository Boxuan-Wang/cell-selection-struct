import torch
import lightning.pytorch as pl
from transformers import BertTokenizer
from ..models.rowcolModel import ColRowClassifier, tokenize
import math
import numpy as np
from ..wikiTable.table import Table
from ..wikiTable.utils import preprocess_cell



class CellClassifier():
    def __init__(
      self,
      cell_model_path,
      db_connection,
      relevant_num_limit:int = 10,
      minimum_score:float = 0.05,
      device:str = None
      
    ):
      self.device = device
      self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
      self.cell_model = ColRowClassifier.load_from_checkpoint(cell_model_path)
      self.cell_model.eval()
      if self.device is not None:
        self.cell_model.to(device)
      self.wiki_db = db_connection
      self.num_limit = relevant_num_limit
      self.min_score = minimum_score
      print("Score model loaded.")
      
    def classify_cells(
      self,
      claim:str,
      table_content:list[list[dict]]
    ) -> Table:
      cell_strings = preprocess_cell(claim, table_content)
      result = []
      for i in range(len(cell_strings)):
        result_row = []
        for j in range(len(cell_strings[i])):
          text = cell_strings[i][j]
          tok = tokenize(text, self.tokenizer)
          if self.device is not None:
            tok.to(self.device)
          with torch.no_grad():
            score = self.cell_model.predict(tok)
          result_row.append(score)
        result.append(result_row)
      
      ret_table = Table(table_content)
      ret_table.mark_cells_by_score_cell_version(result, self.num_limit,self.min_score)
      
      return ret_table
    
    def classify_table_from_id(
      self,
      claim:str,
      table_title:str,
      table_id:int
    ):
      table_content = self.wiki_db.query_wiki_table(table_title,table_id)
      return self.classify_cells(claim,table_content)

    