import torch
from transformers import AutoConfig
from .model.tokenizer import CustomT5TokenizerFast
from .model.modeling_t5 import T5ForConditionalGeneration
from .preprocess.table_linearization import linearize_table_with_index
from ..wikiDatabase.wikiConnection import WIKI_connection
from ..feverous_utils import sanitise_link_format


class TextGenerater:
    def __init__(self, model_path):
        # lattice_config = AutoConfig.from_pretrained("t5_small")
        self.lattice_model = T5ForConditionalGeneration.from_pretrained("t5-small")
        self.lattice_tokenizer = CustomT5TokenizerFast.from_pretrained("t5-small",use_fast=True)
        self.lattice_model.load_state_dict(torch.load(model_path,map_location = torch.device('cuda')))
        self.lattice_model.eval()
    

    def sanitise_table_content(self,table_content):
        """
        Sanitise table content so that the hyper-links are free of '[[]]' format
        """
        for cell_row in table_content:
            for cell in cell_row:

                cell['value'] = sanitise_link_format(cell['value'])
                cell['row_span'] = int(cell['row_span'])
                cell['column_span'] = int(cell['column_span'])

        return table_content
    
    def __preprocess_function__(
        self,
        table:dict, 
        table_page_title: str,
        table_section_title: str,
        highlighted_cells: list[list[int]]) -> dict:
        
        table_metadata_str, type_ids, row_ids, col_ids = linearize_table_with_index(
                table=table,
                cell_indices=highlighted_cells,
                table_page_title=table_page_title,
                table_section_title=table_section_title,
                order_cell=True)
        # example: {text,type_ids, col_ids, row_ids}
        prefix = ""
        tokenizer = self.lattice_tokenizer
        max_source_length = 512
        padding = "max_length"
        max_target_length = 128
        ignore_pad_token_for_loss = True


        inputs = table_metadata_str
        model_inputs = tokenizer(inputs, max_length=max_source_length, padding=padding, truncation=True,
                                    return_offsets_mapping=True,
                                return_tensors='pt')


        model_inputs["type_ids"] = type_ids
        model_inputs["row_ids"] = row_ids
        model_inputs["col_ids"] = col_ids

        del model_inputs["offset_mapping"]

        return model_inputs
    
    def convert(
        self, 
        table:dict,
        highlighted_cells: list[list[int]]
    ) -> str:
        table_content = table["table"]
        table_content = self.sanitise_table_content(table_content)

        table_page_title = table["page_title"]
        table_section_title = table["section_title"]

        model_inputs = self.__preprocess_function__(table_content,table_page_title,table_section_title,highlighted_cells)
        model_outputs = self.lattice_model.generate(
            model_inputs.input_ids,
            attention_mask=model_inputs["attention_mask"],
            max_length = 100,
            num_beams = 4)

        result_str = ""
        for i in range(len(model_outputs)):
            segment_result = self.lattice_tokenizer.decode(model_outputs[i], skip_special_tokens=True)

            if segment_result.strip() == '':
                break
            result_str += segment_result
            
            # print("Evidence text: ", result_str)
            return result_str
    
    def generate_grouped_by_row(
        self,
        table:dict,
        hightlighted_cells: list[list[int]]
    ) -> list[str]:
        """Group selected cells by row. Generate a sentence for each group.

        Args:
            table (dict): table content, table title, section title
            hightlighted_cells (list[list[int]]): highlighted cells

        Returns:
            list[str]: One sentence for each row including selected cells
        """
        num_row = len(table["table"])
        group_list = [None]*num_row
        for cell_id in hightlighted_cells:
            (x,y) = cell_id
            if x >= num_row:
                # ignore index error
                continue
            if group_list[x] is None:
                group_list[x] = [[x,y]]
            else:
                group_list[x].append([x,y])
        
        ret = []
        for group in group_list:
            if group is not None:
                ret.append(self.convert(table,group))

        return ret


# test code for generater

# def test_generater(
#     db_path,
#     model_path,
#     title_test,
#     table_id,
#     selected_cells
# ):
#     test_generater = TextGenerater(model_path)
#     db_test = WIKI_connection(db_path)
    
#     table_content_test = db_test.query_wiki_table(title_test,table_id)
#     table_dict_test = {
#         "table":table_content_test,
#         "page_title":title_test,
#         "section_title":title_test}
#     test_result = test_generater.convert(table_dict_test,selected_cells)
#     test_result_row = test_generater.generate_grouped_by_row(table_dict_test, selected_cells)
    
#     return test_result, test_result_row

# if __name__ == "__main__":
#     db_path = ""
#     lattice_model_path = ""
#     title_test = 'Algebraic logic'
#     table_id = 0
#     selected_cells_test = [[1,0],[1,1],[2,0],[2,1],[3,0],[3,1],[4,1]]
    
#     result, result_row = test_generater(
#         db_path,
#         lattice_model_path,
#         title_test,
#         table_id,
#         selected_cells_test)
    
#     print("Individual: ", result)
#     print("Group by row: ", " ".join(result_row))