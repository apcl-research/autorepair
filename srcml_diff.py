import pickle
import diff_match_patch as dmp_module
import argparse
import os
#srcml_dir = 'srcml_prediction_800k'
#decoded_code_filename = 'decoded_code.pkl'


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

# the highlight_differences() method shows blue for the correct bit and red for the incorrect bit, parts that are the same are in the default color
def highlight_differences(text1, text2):
    dmp = dmp_module.diff_match_patch()
    diffs = dmp.diff_main(text1, text2)
    dmp.diff_cleanupSemantic(diffs)

    highlighted_text = ""
    for op, data in diffs:
        if op == dmp.DIFF_EQUAL:
            highlighted_text += data
        elif op == dmp.DIFF_DELETE:
            highlighted_text += '\033[94m' + data + '\033[0m'
        elif op == dmp.DIFF_INSERT:
            highlighted_text += '\033[91m' + data + '\033[0m'

    return highlighted_text


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--srcml-dir', type=str, default='srcml_prediction_800k')
    parser.add_argument('--decoded-code-filename', type=str, default='decoded_code.pkl')
    parser.add_argument('--num-of-function', type=int, default=30)
    parser.add_argument('--load-bug-code', action='store_true', default=False)
    parser.add_argument('--bug-code-filename', type=str, default='./q90_bug_code/bug_code.pkl')
    args = parser.parse_args()
    
    srcml_dir = args.srcml_dir
    decoded_code_filename = args.decoded_code_filename
    load_bug_code = args.load_bug_code
    num_of_function = args.num_of_function
    bug_code_filename = args.bug_code_filename



    decoded_codes = pickle.load(open(f'{srcml_dir}/{decoded_code_filename}', 'rb'))
    q90codes = pickle.load(open('/nublar/datasets/jm52m/q90fundats-j1.pkl', 'rb'))
    fids = list(decoded_codes.keys())
    total_num_of_functions = len(list(decoded_codes.keys()))
    total_num_of_group = int(total_num_of_functions / num_of_function)
     
    if(not load_bug_code):
        for i in range(total_num_of_group):
            for fid  in fids[(num_of_function * i):num_of_function * (i +1)]:
                print("==================================")
                diff = highlight_differences(decoded_codes[fid], q90codes[fid])
                print(f"ref:\n{q90codes[fid]}") # reference code
                print(f"decoded code:\n{decoded_codes[fid]}") # decoded code
                print(f"diff:\n{diff}") # hilight differnece between predicted code and reference
                print("==================================")
            os.system("/bin/bash -c 'read -s -n 1 -p \"Press any key to continue...\"'")
    else:

        bug_codes = pickle.load(open(bug_code_filename, 'rb'))
        for i in range(total_num_of_group):
            for fid  in fids[(num_of_function * i):num_of_function * (i +1)]:
                diff = highlight_differences(decoded_codes[fid], q90codes[fid])
                print("==================================")
                print(f"ref:\n{q90codes[fid]}") # reference code
                print(f"decoded code:\n{decoded_codes[fid]}") # decoded code
                print(f"diff:\n{diff}") # hilight differnece between predicted code and reference
                print(f"bug code:\n{bug_codes[fid]}")
                bug_code_pred_diff = highlight_differences(decoded_codes[fid], bug_codes[fid])
                print(f"difference between bug code and decoded code:\n{bug_code_pred_diff}") 
                bug_code_ref_diff = highlight_differences(q90codes[fid], bug_codes[fid])
                print(f"difference between bug code and decoded code:\n{bug_code_ref_diff}")

                print("==================================")
            os.system("/bin/bash -c 'read -s -n 1 -p \"Press any key to continue...\"'")


    





