class Cell:
  def __init__(self, wiki_result:dict):
    """
    wiki_result: containing fields: id, value, column_span, row-span, is_header
    """
    self.id = wiki_result['id']
    self.value = wiki_result['value']
    self.col_span = int(wiki_result['column_span'])
    self.row_span = int(wiki_result['row_span'])
    self.is_header = wiki_result['is_header']

    self.row_marked = False
    self.col_marked = False

    self.colour = 'white'

  def generate_HTML(self) -> str:
    """
    Generate HTML string that represents a cell.
    """
    ret = "<"
    # set header/noraml cell
    if self.is_header:
      starter = "th"
    else:
      starter = "td"
    ret += starter
    ret += " "
    # set col/row span
    ret += f"colspan=\"{self.col_span}\" "
    ret += f"rowspan=\"{self.row_span}\" "
    # set colour
    if self.colour != 'white':
      ret += f"style=\"background-color: {self.colour}\">"
    elif self.row_marked and self.col_marked:
      ret += "style=\"background-color: red\">"
    else:
      ret += ">"
    # set cell value
    ret += self.value
    # end
    ret += f"</{starter}>"

    return ret

  def mark_row(self):
    self.row_marked = True
    if self.col_marked:
        self.colour = 'red'
    
  def mark_col(self):
    self.col_marked = True
    if self.row_marked:
        self.colour = 'red'


  def selected(self) -> bool:
    return self.colour == 'red'

  def set_colour(self,new_colour:str):
    self.colour = new_colour
