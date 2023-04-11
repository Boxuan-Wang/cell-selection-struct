from ..classifiers.scoreClassifier import ScoreClassifier
from ..classifiers.cellClassifier import CellClassifier
from ..textGenerater.TtTGeneration import TextGenerater
from ..wikiDatabase.wikiConnection import WIKI_connection
# from wikiTable.table import Table
from ..feverous_utils import parseEvidence
# from tqdm import tqdm
import six
import json
import argparse
from tqdm import tqdm


def evaluate_score_model(
    test_data_path:str,
    store_path:str,
    score_classifier:ScoreClassifier,
    cell_classifier:CellClassifier,
    text_generater:TextGenerater,
    db_connection:WIKI_connection,
    max_accept_table_size:int = 400,
    pretesting:bool=False
) -> None:
      
    with open(store_path, "w") as output_file:
        with open(test_data_path, "r",encoding="utf-8") as test_data_file:
            for i,line in tqdm(enumerate(test_data_file)):
                if pretesting and i > 5:
                    # end loop if in pretest mode
                    break
                line = six.ensure_text(line, "utf-8")
                json_example = json.loads(line)
                claim = json_example['claim']
                if claim == "":
                    # skip empty line
                    continue            
                evidence = json_example['evidence']
                # todo: put parseEvidence somewhere in a util file
                evidence_dict = parseEvidence(evidence)
                if len(evidence_dict.keys())==0:
                    # ignore claim with tabular evidence
                    continue
                for table_key in evidence_dict.keys():
                    # handle annotation data
                    relevants = evidence_dict[table_key]
                    relevant_ids = []
                    for relevant_cell in relevants:
                        row = int(relevant_cell.split('_')[-2])
                        col = int(relevant_cell.split('_')[-1])
                        relevant_ids.append([row,col])
                    
                    (title,table_id) = table_key
                    table_content = db_connection.query_wiki_table(title, table_id)
                    if sum(len(x) for x in table_content) > max_accept_table_size:
                        # skip large tables for time/memory saving
                        break
                    
                    table_dict = {"table":table_content, "page_title":title, "section_title": title}
                    
                    # inference on row/col model
                    marked_table_rowcol = score_classifier.classify_cells(claim, table_content)
                    selected_cells_rowcol = marked_table_rowcol.get_marked_cell_ids()
                    
                    # inference on cell model
                    marked_table_cell = cell_classifier.classify_cells(claim, table_content)
                    selected_cells_cell = marked_table_cell.get_marked_cell_ids()
                    
                    # generate a evidence for each row (row/col model)
                    evidence_sentences_by_row = text_generater.generate_grouped_by_row(table_dict,selected_cells_rowcol)
                    evidence_sentence_all_in_one = text_generater.convert(table_dict,selected_cells_rowcol)
                    
                    #generate evidence for cell model
                    evidence_by_row_cell_model = text_generater.generate_grouped_by_row(table_dict,selected_cells_cell)
                    evidence_all_in_one_cell_model = text_generater.convert(table_dict,selected_cells_cell)
                    
                    result_dict = {'claim': claim }
                    result_dict['id'] = json_example['id']
                    result_dict['table_id'] = table_id
                    result_dict['table_title'] = title
                    result_dict['annotated_cells'] = relevant_ids
                    
                    result_dict['selected_cells_rowcol'] = selected_cells_rowcol
                    result_dict['evidence_sentences_by_row_rowcol'] = evidence_sentences_by_row
                    result_dict['evidence_sentence_single_rowcol'] = evidence_sentence_all_in_one
                    
                    result_dict['selected_cells_cell'] = selected_cells_cell
                    result_dict['evidence_sentences_by_row_cell'] = evidence_by_row_cell_model
                    result_dict['evidence_sentence_single_cell'] = evidence_all_in_one_cell_model
                    
                    
                    output_file.write(json.dumps(result_dict,ensure_ascii=False) + "\n")
    print("Finish evaluation.")
                                 
# if __name__ == "__main__":
#     # todo: add arg parser to the function
#     parser = argparse.ArgumentParser(description="The function to evaluate cell selection model.")
#     parser.add_argument('--test_path', '-t', type=str, help="The path to test dataset.")
#     parser.add_argument('--store_path', '-s', type=str, help='Path to store the evaluation result')
#     parser.add_argument('--db_path', '-d', type=str, help='The path to WIKI database.')
#     parser.add_argument('--ttt_path',type=str, help='The path to table-to-text generation.')
#     parser.add_argument('--row_score','-r', type=str, help='The path to scoring rows')
#     parser.add_argument('--min_score', type=float, default=0.05, help='The minimum score of a relevant cell')
#     parser.add_argument('--max_num_relevant',default=10, type=int, help='Max number of relevant cells in a table')
#     parser.add_argument('--col_score','-c',type=str,help='The path to scoring column model')
#     parser.add_argument('--max_table_size', '-m', default=400, type=int, help='Maximum size of table the model allows')
#     parser.add_argument('--pretesting', '-p', default=False, action='store_true')
#     args = parser.parse_args()
    
#     db_connection = WIKI_connection(args.db_path)
#     score_classifier = ScoreClassifier(
#         args.row_score,
#         args.col_score, 
#         db_connection,
#         minimum_score=args.min_score,
#         relevant_num_limit= args.max_num_relevant
#         )
#     ttt_model = TextGenerater(args.ttt_path)
    
#     evaluate_score_model(
#         args.test_path,
#         args.store_path,
#         score_classifier,
#         ttt_model,
#         db_connection,
#         args.max_table_size,
#         pretesting=args.pretesting)