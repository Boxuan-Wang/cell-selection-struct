def render_table(table_content:list[list[dict]]):
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
        
    return rendering_table

def preprocess_row(
        claim:str,
        table_content:list[list[dict]]
    ) -> list[str]:
        rendering_table = render_table(table_content)
        row_strings = ['_'.join(row) for row in rendering_table]
        row_strings = [claim + "[SEP]" + s for s in row_strings]
        return row_strings
    
def preprocess_col(
    claim:str,
    table_content:list[list[dict]]
) -> list[str]:
    rendering_table = render_table(table_content)
    rendering_table = list(zip(*rendering_table))
    col_strings = ['_'.join(row) for row in rendering_table]
    col_strings = [claim + "[SEP]" + s for s in col_strings]
    return col_strings

def preprocess_cell(
    claim: str,
    table_content:list[list[dict]]
) -> list[list[str]]:
    '''
    [Claim] + [headers] + [cell value]
    for cell with multi row/col span, [headers] are defined for their first 
    row unit/ column unit.
    the first two cells in the corresponing row/col are considered as headers.
    '''
    cell_strings = []
    rendering_table = render_table(table_content)
    for i in range(len(table_content)):
        cell_strings_in_row = []
        col_index_cursor = 0
        row_headers = [table_content[i][0]['value']]
        if len(table_content[i]) >= 2:
            row_headers.append(table_content[i][1]['value'])
        for j in range(len(table_content[i])):
            col_headers = [rendering_table[0][col_index_cursor]]
            if len(rendering_table) > 1:
                col_headers.append(rendering_table[1][col_index_cursor])
            col_index_cursor += int(table_content[i][j]['column_span'])
            cell_str = claim + '[SEP]' + "_".join(row_headers+col_headers+[table_content[i][j]['value']])
            cell_strings_in_row.append(cell_str)
        cell_strings.append(cell_strings_in_row)
    return cell_strings