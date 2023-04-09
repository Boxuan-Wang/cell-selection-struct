def preprocess_row(
        claim:str,
        table_content:list[list[dict]]
    ) -> list[str]:
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
              continue
        
        row_strings = ['_'.join(row) for row in rendering_table]
        row_strings = [claim + "[SEP]" + s for s in row_strings]
        return row_strings
    
def preprocess_col(
    claim:str,
    table_content:list[list[dict]]
) -> list[str]:
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
            continue
        
    rendering_table = list(zip(*rendering_table))
    col_strings = ['_'.join(row) for row in rendering_table]
    col_strings = [claim + "[SEP]" + s for s in col_strings]
    return col_strings