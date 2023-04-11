import queue
from typing import List, Tuple
from datetime import datetime
from cell import Cell


class Table: 
  def __init__(self,wiki_result: List[List[dict]]):
    """
    wiki_result: the result of table-content in wiki database
    """
    self.cell_table = []
    self.rendering_table = []

    for result_row in wiki_result:
      new_row = []
      for result_cell in result_row:
        new_cell = Cell(result_cell)
        new_row.append(new_cell)
      self.cell_table.append(new_row)
    
    # The following code creates a rendering table, corresponding to how the table looks like
    # find the width and height of table
    width = 0
    for j in range(len(self.cell_table[0])):
      width += int(self.cell_table[0][j].col_span)
    height = len(self.cell_table)

    self.rendering_table = [[None for _ in range(width)]for _ in range(height)]
    # resolve row span
    for i in range(height):
      wiki_table_row = self.cell_table[i]
      col_to_write = 0
      for j in range(len(wiki_table_row)):
        cell = wiki_table_row[j]
        while self.rendering_table[i][col_to_write] is not None:
          # taken by previous line
          # go to the next cell
          col_to_write += 1
        assert col_to_write < width
        # write to rendering_table
        try:
          for i_write in range(int(cell.row_span)):
            for j_write in range(int(cell.col_span)):
              if col_to_write +j_write < width:
                self.rendering_table[i+i_write][col_to_write+j_write] = cell
        except IndexError:
          # todo: find a better way to record error
          print("IndexError")
          print(self.cell_table)



  # find a specific cell
  # row/col are in the unit of span
  def find_cell(self, row:int, col:int) -> Cell:
    try:
      ret = self.rendering_table[row][col]
    except IndexError:
      # todo: find a better way to record error
      print("IndexError")
      print(row,col)
    return ret

  def set_cell_colour(self, location:Tuple[int,int], colour:str='white'):
    row,col = location
    try:
      op_cell = self.cell_table[row][col]
      op_cell.set_colour(colour)
    except IndexError:
      # todo: find a better way to record error
      print("INDEX ERROR")
      print(f"Position ({row},{col})")


  def mark_cells(self, cells:List[Tuple[int,int]]):
    for loc in cells:
      x,y = loc
      cell = self.find_cell(x,y)
      cell.set_colour('red')

  def mark_row(self, row_ids:List[int]):
    for row_id in row_ids:

      for cell in self.cell_table[row_id]:
        cell.mark_row()
    
  def mark_col(self,col_ids:List[int]):

    for row in self.cell_table:
      for cell in row:
        col_id = int(((cell.id).split("_"))[-1])
        if col_id in col_ids:
          cell.mark_col()

  def mark_cells_by_score(self, scores:List[List[int]], num_limit:int, min_score:float):
    marked_cell_num = 0
    score_queue = queue.PriorityQueue()
    for i in range(len(scores)):
      for j in range(len(scores[i])):
        score_queue.put((1-scores[i][j],[i,j]))
    while marked_cell_num < num_limit:
      if score_queue.empty():
        break
      else:
        value,id = score_queue.get()
        if value > 1 - min_score:
          break
        x,y = id
        op_cell = self.find_cell(x,y)
        if op_cell.selected():
          continue
        else:
          op_cell.set_colour('red')
          marked_cell_num += 1
  
  '''
  The version for cell classification. Here, scores are in the unit of cells (not in span), i.e. different rows may have different lengths
  '''
  def mark_cells_by_score_cell_version(self, scores:List[List[int]], num_limit:int, min_score:float):
    marked_cell_num = 0
    score_queue = queue.PriorityQueue()
    for i in range(len(scores)):
      for j in range(len(scores[i])):
        score_queue.put((1-scores[i][j],[i,j]))
    while marked_cell_num < num_limit:
      if score_queue.empty():
        break
      else:
        value,id = score_queue.get()
        if value > 1 - min_score:
          break
        x,y = id
        try:
          op_cell = self.cell_table[x][y]
        except IndexError:
          # todo: find a better way to record error
          print("INDEX ERROR")
          print(f"Position ({x},{y})")
        if op_cell.selected():
          continue
        else:
          op_cell.set_colour('red')
          marked_cell_num += 1


  def generate_HTML(self) -> str:
    ret = "<table border = \"1px solid\">"
    for table_row in self.cell_table:
      ret += "<tr>"
      for table_cell in table_row:
        ret += table_cell.generate_HTML()
    ret += "</table>"
    return ret
  
  def compare_annonation(self, annonatated_cells:List[str]) -> Tuple[int,int,int,int]:
    t_p, t_n, f_p, f_n = 0, 0, 0, 0
    annonatated_cells = ["_".join(cell.split("_")[1:]) for cell in annonatated_cells]
    for row in self.cell_table:
      for cell in row:
        if cell.selected() and cell.id in annonatated_cells:
          t_p += 1
        elif cell.selected() and not (cell.id in annonatated_cells):
          f_p += 1
        elif not(cell.selected()) and not (cell.id in annonatated_cells):
          t_n += 1
        else:
          f_n += 1
    return t_p, t_n, f_p, f_n

  # path the folder to store the HTML file
  # todo: delete if not used
  def store_HTML(self, path:str, file_name:str):
    time = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = file_name + "_" + time + ".html"
    full_path = path + "/" + file_name
    with open(full_path,"w") as f:
      f.write(self.generate_HTML())
      print(f"Write to {full_path}.")
    
  def get_marked_cell_ids(self) -> list[list[int]]:
    result = []
    for i in range(len(self.cell_table)):
      row = self.cell_table[i]
      for j in range(len(row)):
        cell = row[j]
        if (cell.row_marked and cell.col_marked) or cell.colour == 'red':
          result.append([i,j])
    return result