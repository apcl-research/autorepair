import pickle
import subprocess
from tqdm import tqdm
import numpy as np
import javalang
import diff_match_patch as dmp_module

srcml_dir = 'srcml_prediction_bug_new'
q90testfidsfile = '/nublar/datasets/jm52m/q90testfids.pkl'
bug_code_ref_file = './data/autorepair/test_bug_code.pkl'
q90codefile = '/nublar/datasets/jm52m/q90fundats-j1.pkl'
exec(open('configurator.py').read())

def detect_syntax_errors(java_code):
    try:
        # Parse the Java code
        tree = javalang.parse.parse(java_code)
        return False # No syntax errors found
    except javalang.parser.JavaSyntaxError as e:
        return True

    except javalang.tokenizer.LexerError:
        return True

def levenshteinDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]

def highlight_differences(text1, text2):
    dmp = dmp_module.diff_match_patch()
    diffs = dmp.diff_main(text1, text2)
    dmp.diff_cleanupSemantic(diffs)

    highlighted_text = ""
    count_all = 0 
    count_equal = 0
    for op, data in diffs:
        count_all += 1
        if op == dmp.DIFF_EQUAL:
            highlighted_text += data
        elif op == dmp.DIFF_DELETE:
            
            count_equal += 1
            highlighted_text += '\033[94m' + data + '\033[0m'
        elif op == dmp.DIFF_INSERT:
            highlighted_text += '\033[91m' + data + '\033[0m'
    if(count_all == count_equal):
        error = True
    else:
        error = False
    return highlighted_text, error

q90testfids = pickle.load(open(q90testfidsfile, 'rb'))
all_bug_code = pickle.load(open(bug_code_ref_file,'rb'))
allcode = pickle.load(open(q90codefile, 'rb'))

count_correct = 0
count_all = 0
count_bug_not_fix = 0
decoded_code_dict = {}
bug_type_count_dict = {"parentheses_left":1, "parentheses_right": 1, "curly_left":1, "curly_right":1, "braket_left":1, "braket_right":1, "semicolon":1}
fixed_bug_type_count_dict = {"parentheses_left":0, "parentheses_right": 0, "curly_left":0, "curly_right":0, "braket_left":0, "braket_right":0, "semicolon":0}
removed_char_map  = {"(":"parentheses_left", ")":"parentheses_right", "{":"curly_left", "}":"curly_right", "[":"braket_left", "]":"braket_right", ";":"semicolon"}
removed_char_name_map  = {"parentheses_left":"(", "parentheses_right":")", "curly_left":"{", "curly_right":"}", "braket_left":"[", "braket_right":"]", "semicolon":";"}
#code_perfect_edit_distance = 0
#code_non_perfect_edit_distance = 0

for fid in tqdm(q90testfids):

    count_all += 1
    
    bug_code = all_bug_code[fid]['bug_code']
    bug_pos = all_bug_code[fid]['bug_pos']
    code_without_bug = allcode[fid]
    removed_char = removed_char_map[code_without_bug[bug_pos]]
    bug_type_count_dict[removed_char] += 1

    code = allcode[fid]

    try:
        with open(f'{srcml_dir}/{fid}.xml', 'r', encoding='utf-8') as f:
            srcml_pred = f.read()
    except:
        continue
    if (srcml_pred == 'none'):
        continue
    try:
        decoded_pred = subprocess.run(['srcml', f'{srcml_dir}/{fid}.xml'],  timeout=5, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8')
    except:
        continue
    

    if( not detect_syntax_errors('public class Dummy { ' + decoded_pred + ' }')):
        
        hilighted_bug_code, iserror = highlight_differences(bug_code, decoded_pred)
        if(iserror):
            count_bug_not_fix += 1
        else:
            count_correct += 1

            fixed_bug_type_count_dict[removed_char] += 1
            

    else:

        count_bug_not_fix += 1

for char_type in list(fixed_bug_type_count_dict.keys()):
    accuracy = fixed_bug_type_count_dict[char_type] / bug_type_count_dict[char_type]
    char_type = removed_char_name_map[char_type]
    print(f"accuracy for {char_type}: {round(accuracy, 2)}") 


print(f'bug fix rate: {round(count_correct / count_all, 2)}')

