import pickle
import subprocess
from tqdm import tqdm
import numpy as np
import javalang




def detect_syntax_errors(java_code):
    try:
        # Parse the Java code
        #print("--", java_code)
        tree = javalang.parser.Parser(java_code)
        tree = tree.parse_type_declaration()
        return "no erro" # No syntax errors found
    except javalang.parser.JavaSyntaxError as e:
        return "error"

q90code = pickle.load(open('/nublar/datasets/jm52m/q90fundats-j1.pkl', 'rb'))

q90fid = list(q90code.keys())

bug_code = {}

for fid in q90fid:

    code = q90code[fid]
    code = 'public class Dummy { ' + code + ' }'
    syntax_pos_list = []
    paren_left = [i for i in range(len(code)) if code.startswith('(', i)]
    paren_right = [i for i in range(len(code)) if code.startswith(')', i)]
    curly_left = [i for i in range(len(code)) if code.startswith('{', i)]
    curly_right = [i for i in range(len(code)) if code.startswith('}', i)]
    semicolon = [i for i in range(len(code)) if code.startswith(';', i)]
    syntax_pos_list.extend(paren_left)
    syntax_pos_list.extend(paren_right)
    syntax_pos_list.extend(curly_left)
    syntax_pos_list.extend(curly_right)
    syntax_pos_list.extend(semicolon)
    pos = random.randint(0,len(syntax_pos_list) - 1)
    code = list(code)
    code[syntax_pos_list[pos]] = ""
    code = ''.join(code)
    #bug_code[fid] = 

    #code = code.replace(code[paren_left[0]], "")
    #code = javalang.tokenizer.tokenize(code)
    #print(code)
#err = detect_syntax_errors(code)
#a = detect_syntax_errors(code)
#print("llll", err)
#for fid in q90fid:
#print(q90fid[0])
