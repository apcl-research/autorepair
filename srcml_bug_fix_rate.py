import pickle
import subprocess
from tqdm import tqdm
import numpy as np
import javalang
import diff_match_patch as dmp_module

srcml_dir = 'srcml_prediction_bug_new'

def detect_syntax_errors(java_code):
    try:
        # Parse the Java code
        #print("--", java_code)
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

q90testfids = pickle.load(open('/nublar/datasets/jm52m/q90testfids.pkl', 'rb'))
all_bug_code = pickle.load(open('./data/autorepair/test_bug_code.pkl','rb'))
allcode = pickle.load(open('/nublar/datasets/jm52m/q90fundats-j1.pkl', 'rb'))

count_correct = 0
count_all = 0
count_input_error = 0
count_error_generating_code = 0
count_bug_not_fix = 0
count_bug_javalang_not_detected = 0
count_perfect = 0
total_distance = 0
bug_fix_total_distance = 0
count_near_perfect = 0
decoded_code_dict = {}
bug_type_count_dict = {"parentheses_left":0, "parentheses_right": 0, "curly_left":0, "curly_right":0, "braket_left":0, "braket_right":0, "semicolon":0}
fixed_bug_type_count_dict = {"parentheses_left":0, "parentheses_right": 0, "curly_left":0, "curly_right":0, "braket_left":0, "braket_right":0, "semicolon":0}
removed_char_map  = {"(":"parentheses_left", ")":"parentheses_right", "{":"curly_left", "}":"curly_right", "[":"braket_left", "]":"braket_right", ";":"semicolon"}
removed_char_name_map  = {"parentheses_left":"(", "parentheses_right":")", "curly_left":"{", "curly_right":"}", "braket_left":"[", "braket_right":"]", "semicolon":";"}

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
        count_input_error += 1
        continue
    if (srcml_pred == 'none'):
        count_input_error += 1
        continue
    try:
        decoded_pred = subprocess.run(['srcml', f'{srcml_dir}/{fid}.xml'],  timeout=5, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8')
    except:
        count_error_generating_code += 1
        continue
    
    d = int(levenshteinDistance(code, decoded_pred))
    total_distance += d

    if( not detect_syntax_errors('public class Dummy { ' + decoded_pred + ' }')):
        
        hilighted_bug_code, iserror = highlight_differences(bug_code, decoded_pred)
        if(iserror):
            count_bug_javalang_not_detected += 1
            count_bug_not_fix += 1
        else:
            count_correct += 1

            fixed_bug_type_count_dict[removed_char] += 1

            if(d == 0):
                count_perfect += 1
            elif(d > 0 and d < 10):
                count_near_perfect += 1
            if(d > 0):
                #hilighted_code, iserror = highlight_differences(code, decoded_pred)
                decoded_code_dict[fid] = decoded_pred

            bug_fix_total_distance += d
    else:

        count_bug_not_fix += 1
bug_code_hilight_file = open(f"{srcml_dr}/decoded_code.pkl", "wb")
pickle.dump(decoded_code_dict, bug_code_hilight_file)
#decoded_code_hilight_file = open("ref_and_decoded_code_hilight.pkl", "wb")
#pickle.dump(decoded_code_hilight, decoded_code_hilight_file)

for char_type in list(fixed_bug_type_dict.keys()):
    accuracy = bug_type_count_dict[char_type] / fixed_bug_type_count[char_type]
    char_type = removed_char_name_map[char_type]
    print(f"accuracy for {char_type}: {round(accuracy, 2)}") 


print(f'total number of functions: {count_all}')
print(f'total number of functions without bugs: {count_correct}')
print(f'bug fix rate: {round(count_correct / count_all, 2)}')
print(f'number of functions with invalid srcml: {count_error_generating_code}')
print(f'number of functions without srcml prediction: {count_input_error}')
print(f'number of functions without fixing bugs: {count_bug_not_fix}')
print(f'number of functions with bugs but not detected by javalang: {count_bug_javalang_not_detected}')
print(f'mean distance: {round(total_distance / count_all, 2)}')
print(f'mean distance when bug is fixed: {round(bug_fix_total_distance / count_correct, 2)}')
print(f'number of perfect samples when bug is fixed: {count_perfect} / {count_correct}')
print(f'perfection rate: {round(count_perfect / count_all, 2)}')
print(f'perfection rate when bug is fixed: {round(count_perfect / count_correct, 2)}') 
print(f'number of near perfect samples when bug is fixed: {count_near_perfect} / {count_correct}')
print(f'near perfection rate: {round(count_near_perfect / count_all, 2)}')
print(f'near perfection rate when bug is fixed: {round(count_near_perfect / count_correct, 2)}')

