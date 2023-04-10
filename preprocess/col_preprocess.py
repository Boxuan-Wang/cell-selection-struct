import pandas as pd
import numpy as np
import json
import os
import apsw
from json import JSONDecodeError
import ast
import csv
from ..wikiDatabase.wikiConnection import WIKI_connection
from ..feverous_utils import parseEvidence


'''
Given a table representation. Return a list of linearized column strings.
'''
def parse_col(table_content)->list:
  # find the width and height of table
  width = 0
  for j in range(len(table_content[0])):
    width += int(table_content[0][j]['column_span'])
  height = len(table_content)

  rendering_table = [[None for _ in range(width)]for _ in range(height)]
  # resolve row span
  for i in range(height):
    wiki_table_row = table_content[i]
    col_to_write = 0
    for j in range(len(wiki_table_row)):
      cell = wiki_table_row[j]
      while rendering_table[i][col_to_write] is not None:
        # taken by previous line
        # go to the next cell
        col_to_write += 1
      assert col_to_write < width
      # write to rendering_table
      try:
        for i_write in range(int(cell['row_span'])):
          for j_write in range(int(cell['column_span'])):
            if col_to_write +j_write < width:
              rendering_table[i+i_write][col_to_write+j_write] = cell['value']
      except IndexError:
        print("***************IndexError*************")
        print(table_content)
  rendering_table = list(zip(*rendering_table))
  row_strings = ['_'.join(row) for row in rendering_table]
  return row_strings

'''
Proprecess the col relevancy for a single evidence table.
Input: claim, table_id, relevant cell ids, db_connection
'''
def preprocess_col_single_table(table_id, relevant_cells, claim, db_connection,):
  csv_rows = []
  (title,ind_table) = table_id
  # query WIKI database to get table content
  table_content = db_connection.query_wiki_table(title,ind_table)
  # find relevant rows
  relevant_cols = set()
  for relevant_cell in relevant_cells:
    col_id = int(relevant_cell.split('_')[-1])
    row_id = int(relevant_cell.split('_')[-2])
    # this is needed because in  table representation in wiki database
    # a cell may have multi column span
    # and will make the col_id a chaos
    if row_id >= len(table_content):
      # row_id index error
      print('*******************')
      print('Row id index error')
      print(f'table id: {table_id}, relevant cell id:{relevant_cell}')
      print('*******************')
      continue
    row_of_the_cell = table_content[row_id]
    if col_id >= len(row_of_the_cell):
      # to avoid index overflow,   some tables in the wiki database are corrupted
      print('*******************')
      print('Column id index error')
      print(f'table id: {table_id}, relevant cell id:{relevant_cell}')
      print('*******************')
      continue
    col_render_id = 0
    for i in range(col_id):
      col_render_id += int(row_of_the_cell[i]['column_span'])
    for i in range(int(row_of_the_cell[col_id]['column_span'])):
      # if the cell covers multiple columns, all columns are regarded as relevant
      relevant_cols.add(col_render_id + i)
  print(relevant_cols)
  processed_strings = parse_col(table_content)
  for i,processed_string in enumerate(processed_strings):
    relevant = i in relevant_cols
    combined_str = claim + '[SEP]' + processed_string
    csv_row = [combined_str,relevant]
    csv_rows.append(csv_row)
  return csv_rows

'''
input: the samples from FEVEROUS, 
path to saved processed strings,
table parser, WIKI database
'''
def preprocess_col(dataset_path:str, save_path:str, db_connection: WIKI_connection)->None:
  # load the dataframe and tidy up
  dataframe = pd.read_json(dataset_path,
                    orient='records',
                    lines=True,
                    dtype={'id':int,'claim':str,'label':str,'evidence':str,'annotator_operation':json,'challenge':str})
  dataframe.dropna()
  dataframe = dataframe[['id','claim','label','evidence']]
  dataframe['evidence'] = dataframe['evidence'].astype('str')
  dataframe = dataframe[(dataframe['label']=='REFUTES')|(dataframe['label']=='SUPPORTS')|(dataframe['label']=='NOT ENOUGH INFO')]

  dataframe['evidence'] = [parseEvidence(e) for e in dataframe['evidence']]
  
  with open(save_path,"w") as f:
    writer = csv.writer(f)
    for i in range(len(dataframe)):
      data_row = dataframe.iloc[i]
      claim = data_row.claim
      evidence = data_row.evidence
      for table_id in evidence.keys():
        relevant_cells = evidence[table_id]
        csv_rows = preprocess_col_single_table(table_id,relevant_cells,claim,db_connection)
        for csv_row in csv_rows:
          print(csv_row)
          writer.writerow(csv_row)