import pickle
import argparse
import os
import random
import diff_match_patch as dmp_module
from tqdm import tqdm

num_of_bugs = 1

q90code = pickle.load(open('/nublar/datasets/jm52m/q90fundats-j1.pkl', 'rb'))
q90testfids = pickle.load(open('/nublar/datasets/jm52m/q90testfids.pkl', 'rb'))

# helpful for checking if character is removed
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--outdir', type=str, default='q90_bug_code')
    
    args = parser.parse_args()

    outdir = args.outdir
    if(not os.path.exists(outdir)):
        os.mkdir(outdir)
    #if(not os.path.exists(f'{outdir}/bug_code')):
    #    os.mkdir(f'{outdir}/bug_code')
    #if(not os.path.exists(f'{outdir}/no_bug_code')):
    #    os.mkdir(f'{outdir}/no_bug_code')
    kk = 0
    test_bug_code_dict = {}
    #no_bug_code_list = []
    for fid in tqdm(q90testfids):
        #if ( kk==1):
        #    break
        #else:
        #    kk +=1
        code = q90code[fid]
        ori_code = q90code[fid]
        syntax_pos_list  = []
        paren_left = [i for i in range(len(code)) if code.startswith('(', i)]
        paren_right = [i for i in range(len(code)) if code.startswith(')', i)]
        curly_left = [i for i in range(len(code)) if code.startswith('{', i)]
        curly_right = [i for i in range(len(code)) if code.startswith('}', i)]
        square_right = [i for i in range(len(code)) if code.startswith(']', i)]
        square_left = [i for i in range(len(code)) if code.startswith('[', i)]
        semicolon = [i for i in range(len(code)) if code.startswith(';', i)]
        syntax_pos_list.extend(paren_left)
        syntax_pos_list.extend(paren_right)
        syntax_pos_list.extend(curly_left)
        syntax_pos_list.extend(curly_right)
        syntax_pos_list.extend(semicolon)
        syntax_pos_list.extend(square_right)
        syntax_pos_list.extend(square_left)
        all_bug_pos = random.sample(range(0, len(syntax_pos_list)-1), num_of_bugs)
        temp = code[:]
        code = list(code)
        for pos in all_bug_pos:
            code[syntax_pos_list[pos]] = " "
            end_pos = len(code)
            start_pos = 0
            bug_pos = syntax_pos_list[pos]
            for i in range(syntax_pos_list[pos], len(code)):
                if (code[i] =='\n'):
                    end_pos = i
                    break
            for i in range(syntax_pos_list[pos], 0, -1):
                if(code[i] == '\n'):
                    start_pos = i
                    break
        ori_code = list(ori_code)
        ori_code_snippet = ori_code[start_pos:end_pos].copy()
        ori_code_snippet = ''.join(ori_code_snippet)
        bug_code_snippet = code[start_pos:end_pos].copy()
        bug_code_snippet = ''.join(bug_code_snippet)
        code = ''.join(code)
        #print(bug_code_snippet)
        #print(ori_code_snippet)
        test_bug_code_dict[fid] = {'bug_code':code, 'bug_code_line':bug_code_snippet, 'patch':ori_code_snippet, 'start_pos': start_pos, 'end_pos':end_pos, 'bug_pos': bug_pos}
    bug_file = open('test_bug_code.pkl', 'wb')
    pickle.dump(test_bug_code_dict, bug_file)
    bug_file.close()



    

