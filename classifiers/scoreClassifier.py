import torch
import lightning.pytorch as pl
from transformers import BertTokenizer
from ..models.rowcolModel import ColRowClassifier, tokenize
import math
import numpy as np
from ..wikiTable.table import Table
from ..wikiTable.utils import preprocess_col,preprocess_row



class ScoreClassifier():
    def __init__(
      self,
      row_model_path,
      col_model_path,
      db_connection,
      relevant_num_limit:int = 10,
      minimum_score:float = 0.05,
      device:str = None
    ):
      self.device = device
      self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
      self.row_model = ColRowClassifier.load_from_checkpoint(row_model_path)
      self.row_model.eval()
      self.col_model = ColRowClassifier.load_from_checkpoint(col_model_path)
      self.col_model.eval()
      if self.device is not None:
        self.col_model.to(self.device)
        self.row_model.to(self.device)
      self.wiki_db = db_connection
      self.num_limit = relevant_num_limit
      self.min_score = minimum_score
      print("Score model loaded.")
    
    def score_rows_in_table(
      self, 
      claim:str,
      table_content:list[list[dict]]
    ) -> list[float]:
      ret = []
      row_strings = preprocess_row(claim,table_content)
      for i,text in enumerate(row_strings):
        tok = tokenize(text, self.tokenizer)
        if self.device is not None:
          tok.to(self.device)
        with torch.no_grad():
          result = self.row_model.predict(tok)
        ret.append(result)
      return ret
    
    def score_cols_in_table(
      self,
      claim:str,
      table_content:list[list[dict]]
    ) -> list[float]:
      ret = []
      col_strings = preprocess_col(claim,table_content)
      for i,text in enumerate(col_strings):
        tok = tokenize(text, self.tokenizer)
        if self.device is not None:
          tok.to(self.device)
        with torch.no_grad():
          result = self.col_model.predict(tok)
        ret.append(result)
      return ret
    
    def classify_cells(
      self,
      claim:str,
      table_content:list[list[dict]]
    ) -> Table:
      row_result = self.score_rows_in_table(claim,table_content)
      col_result = self.score_cols_in_table(claim,table_content)
      cell_scores = np.outer(row_result,col_result).tolist()
      
      ret_table = Table(table_content)
      ret_table.mark_cells_by_score(cell_scores, self.num_limit,self.min_score)
      
      return ret_table
    
    def classify_table_from_id(
      self,
      claim:str,
      table_title:str,
      table_id:int
    ):
      table_content = self.wiki_db.query_wiki_table(table_title,table_id)
      return self.classify_cells(claim,table_content)

    