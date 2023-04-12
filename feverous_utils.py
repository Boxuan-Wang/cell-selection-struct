import json
from json import JSONDecodeError
import ast

# define util functions to parse the evidence from FEVEROUS dataset

# take in a string that represents a set of evidence represeantation
# output the array of string representation
def parseEvidenceList(evidenceStr):
  ret = []
  forward_bracket = 0
  backward_bracket = 0
  last_break_point = 0
  for i in range(1,len(evidenceStr)):
    if evidenceStr[i]=='{': 
      forward_bracket = forward_bracket + 1
    elif evidenceStr[i]=='}':
      backward_bracket = backward_bracket + 1
      if forward_bracket == backward_bracket:
        ret.append(evidenceStr[last_break_point+1:i+1])
        last_break_point = i+1
  return ret

# classify the type of evidence
def classifyEvidence(evidence_id):
  l = evidence_id.split('_')
  if l[1]=='cell':
    ret = 'cell'
  elif l[1]=='header' and l[2]=='cell':
    ret = 'header'
  elif l[1]=='sentence':
    ret = 'sentence'
  else:
    ret = 'other'
  return ret

def parseEvidence(evidenceStr):
  evidence_list = parseEvidenceList(evidenceStr)
  
  evidence_dict = {}
  for string in evidence_list:
    ori_string = string
    try:
      # evidence = json.loads(string.strip())
      evidence = ast.literal_eval(string.strip())
    except JSONDecodeError:
      print(f"ERROR!When parsing evidence: {string}")
      print(ori_string)
      # f.write(string + "\n")
      # error = error + 1
      continue
    evidence_id = evidence['content'] # may need conversion
    evidence_context = evidence['context']
    
    for cell in evidence_id:
      l = cell.split('_')
      if classifyEvidence(cell)=='cell' or classifyEvidence(cell)=='header':
        # filter the list to cell evidence only
        context_list = evidence_context[cell]
        title = context_list[0].split('_')[-2]
        table_ind = l[-3]
        headers = [s for s in context_list if not s.endswith('title')]
        if (title,table_ind) in evidence_dict:
          evidence_dict[(title,table_ind)].append(cell)
        else:
          evidence_dict[(title,table_ind)] = []
          evidence_dict[(title,table_ind)].append(cell)
  return evidence_dict

# delete the link format in the WIKI database
# the link format is like   '[[EFL_Cup|League Cup]]'
def sanitise_link_format(text:str) -> str:
  while True:
    link_loc = text.find('[[')
    if link_loc == -1:
      break
    link_end = text.find(']]')
    link_mid = text.find('|', link_loc, link_end)
    if link_end==-1 or link_mid==-1:
        # this is a not expected case, break to avoid dead loop
        return text
    text = text[:link_loc] + text[link_mid+1 : link_end] + text[link_end+2:]
  
  return text

# return the evidence set that uses sentence evidence only
# return: list[list[str]], sets of sentence evidence (each list[str] is a set of evidence)
def parseSentenceEvidenceOnly(evidenceStr:str) -> list[list[str]]:
  evidence_list = parseEvidenceList(evidenceStr)
  ret = []
  for string in evidence_list:
    ori_string = string
    try:
      evidence = ast.literal_eval(string.strip())
    except JSONDecodeError:
      print(f"ERROR!When parsing evidence: {string}")
      print(ori_string)
      
    evidence_id = evidence['content']
    
    pure_sentence = True
    evidence_set = []
    for item in evidence_id:
      l = item.split('_')
      if l[-2]!= 'sentence':
        pure_sentence = False
        break
      evidence_set.append(item)
  if pure_sentence:
    ret.append(evidence_set)
  return ret
      
        
      