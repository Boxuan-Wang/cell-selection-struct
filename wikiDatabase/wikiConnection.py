import json
import apsw


class WIKI_connection():
  def __init__(self, db_path):
    self.connection = apsw.Connection(db_path)
    print("Connect to WIKI db.")

  def query_wiki_whole_table(self,title,local_table_id):
    # title_id: str, such as, 'Michael Folivi'; 
    # local_table_id: int
    cur = self.connection.cursor()
    res = cur.execute("SELECT data from wiki where id = " + "\"" + title + "\"")
    page = (res.fetchall())[0][0]
    page = json.loads(page)
    table_id = "table_"+ str(local_table_id)
    table_content = page[table_id]
    return table_content

  def query_wiki_table(self,title,local_table_id):
    # title_id: str, such as, 'Michael Folivi'; 
    # local_table_id: int
    cur = self.connection.cursor()
    res = cur.execute("SELECT data from wiki where id = " + "\"" + title + "\"")
    page = (res.fetchall())[0][0]
    page = json.loads(page)
    table_id = "table_"+ str(local_table_id)
    table_content = page[table_id]['table']
    return table_content
  
  def query_wiki_table_from_cell_id(self,cell_id):
    l = cell_id.split('_')
    title = l[0]
    cur = self.connection.cursor()
    res = cur.execute("SELECT data from wiki where id = " + "\"" + title + "\"")
    page = (res.fetchall())[0][0]
    page = json.loads(page)
    table_id = "table_" + l[-3]
    table_content = page[table_id]['table']
    return table_content

  def queryWikiCell(self,cell_id):
    l = cell_id.split('_')
    row_id = (int)(l[-2])
    col_id = (int)(l[-1])
    table_content = self.query_wiki_table_cell_id(cell_id)
    cell_content = table_content[row_id][col_id]
    cell_value = cell_content['value']
    return cell_value