import math
import numpy as np
import tensorflow as tf
from wikiTable.table import Table
from wikiTable.untils import preprocess_col,preprocess_row


class ScoreClassifier():
    def __init__(
      self,
      row_model_path,
      col_model_path,
      # todo: implement wikiConnection class
      db_connection,
      relevant_num_limit:int = 10,
      minimum_score:float = 0.05
    ):
      with tf.device('job:localhost'):
        # todo: may need to change device
        self.row_model = tf.saved_model.load(row_model_path)
        self.col_model = tf.saved_model.load(col_model_path)
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
      col_strings = preprocess_row(claim,table_content)
      for i,text in enumerate(col_strings):
        with tf.device('/job:localhost'):
          # todo: may need to change device
          result = self.col_model([text])
        result = (result.numpy())[0][0]
        result = 1/(1+math.exp(-result))
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
        with tf.device('/job:localhost'):
          # todo: may need to change device
          result = self.col_model([text])
        result = (result.numpy())[0][0]
        result = 1/(1+math.exp(-result))
        ret.append(result)
      return ret
    
    def classify_cells(
      self,
      claim:str,
      table_content:list[list[dict]]
    ) -> Table:
      row_result = self.classify_table_by_row(claim,table_content)
      col_result = self.classify_table_by_col(claim,table_content)
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

    