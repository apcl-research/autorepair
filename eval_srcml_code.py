import pickle
import subprocess
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import javalang
import diff_match_patch as dmp_module
import statistics
srcml_dir = 'srcml_predictions'

def detect_syntax_errors(java_code):
    try:
        # Parse the Java code
        tree = javalang.parse.parse(java_code)
        return None  # No syntax errors found
    except javalang.parser.JavaSyntaxError as e:
        return e
    except javalang.tokenizer.LexerError as e:
        return e

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
    for op, data in diffs:
        if op == dmp.DIFF_EQUAL:
            highlighted_text += data
        elif op == dmp.DIFF_DELETE:
            highlighted_text += '\033[94m' + data + '\033[0m'
        elif op == dmp.DIFF_INSERT:
            highlighted_text += '\033[91m' + data + '\033[0m'

    return highlighted_text

q90code = pickle.load(open('/nublar/datasets/jm52m/q90fundats-j1.pkl', 'rb'))
q90testsrcml = pickle.load(open('/nublar/datasets/jm52m/q90testfids_srcml.pkl', 'rb'))
q90testfids = pickle.load(open('/nublar/datasets/jm52m/q90testfids.pkl', 'rb'))
q90decodedcode = pickle.load(open(f'{srcml_dir}/decoded_code_new.pkl', "rb"))

results = dict()

se = 0 # count syntax errors

decoded_code_dict =  {}
code_levenshtein_distance_list = []
srcml_levenshtein_distance_list = []
code_edit_distance_greater_than_zero_count = 0
code_edit_distance_greater_than_zero = 0
srcml_edit_distance_greater_than_zero_count = 0
srcml_edit_distance_greater_than_zero = 0
all_srcml_edit_distance = 0
code_len = 0
srcml_len = 0
count_perfect_srcml = 0

for fid in tqdm(q90testfids[:5]):
  
  #print(f'{fid}\t', end='', flush=True)
  
    #try:
    #    with open(f'{srcml_dir}/{fid}.xml', 'r', encoding='utf-8') as f:
    #        srcml_pred = f.read()
    #except:
        #print('text')
    #    continue

    #if srcml_pred == 'none':
    #    results[fid] = -1
    #print('-1')
    #    continue

    #srcml_ref = q90testsrcml[fid]
    #srcml_ref = srcml_ref.strip()
    #srcml_pred = srcml_pred.strip()
    
    ref = q90code[fid]
  
    #err = detect_syntax_errors('public class Dummy { ' + ref + ' }')
  
    #if err != None:
    #    se += 1
  #  print(f'{ref}\n{err.description}')
    #try: 
    #    decoded_pred = subprocess.run(['srcml', f'{srcml_dir}/{fid}.xml'], timeout=5, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8')
    #except:
    #    results[fid]= -2
    #    decoded_code_dict[fid] = "error"
    #    continue

    #if "Error" in decoded_pred:
    #    results[fid] = -2
    #print('-2')
    #     continue
  
    #srcml_edit_distance = levenshteinDistance(srcml_ref, srcml_pred)
    decoded_code = q90decodedcode[fid]
    if(decoded_code == "error"):
        results[fid] = -2
        continue
    elif(decoded_code =="none srcml"):
        results[fid] = -1
        continue
    split_decoded_code = list(decoded_code)
    code_len += len(split_decoded_code)
    #split_pred_srcml = list(srcml_pred)
    #srcml_len += len(split_pred_srcml)

    d = levenshteinDistance(ref, decoded_code)
    code_levenshtein_distance_list.append(d)
    #srcml_levenshtein_distance_list.append(srcml_edit_distance)
    if( d > 0):
        code_edit_distance_greater_than_zero_count += 1
        code_edit_distance_greater_than_zero += int(d)
        #decoded_code_dict[fid] = decoded_pred
    #if(srcml_edit_distance > 0):
    #    srcml_edit_distance_greater_than_zero_count += 1
    #    srcml_edit_distance_greater_than_zero += int(srcml_edit_distance)
    #elif(srcml_edit_distance == 0):
    #    count_perfect_srcml += 1
    
  # uncommment the following to show the differences between the reference and decoded predicted code
  # the highlight_differences() method shows blue for the correct bit and red for the incorrect bit, parts that are the same are in the default color
    #if d > 0:
    #    print(ref)
    #    print(decoded_pred)
    #    print(highlight_differences(ref, decoded_pred))
    #quit()

    results[fid] = int(d)
    #all_srcml_edit_distance += int(srcml_edit_distance) 
  #print(f'{d}')

#pickle.dump(decoded_code_dict, open(f'{srcml_dir}/decoded_code.pkl', 'wb'))

n = 0
c = 0
l = 0
p = 0
e1 = 0
e2 = 0

for fid in results:
  res = results[fid]
  
  if res >= 0:
    n += res
    c += 1
    
  if res == 0:
    p += 1
  elif res > 0 and res < 10:
    l += 1
  elif res == -1:
    e1 += 1
  elif res == -2:
    e2 += 1
    
#print(f'total number of valid samples:\t{c}')              # total number of valid samples
print(f'sum of edit distance between reference code and decoded code:\t{n}')              # sum of all edit distances
print(f'mean edit distance between reference code and decoded code:\t{round(n/c, 2)}') # mean edit distance
print(f'mean edit distance between reference code and decoded code for non perfect samples:\t{round(code_edit_distance_greater_than_zero/code_edit_distance_greater_than_zero_count, 2)}')
print(f'median edit distance between reference code and decoded code:\t{statistics.median(code_levenshtein_distance_list)}')

#print(f'sum of edit distance between reference srcml and decoded srcml:\t{all_srcml_edit_distance}')              # sum of all edit distances
#print(f'mean edit distance between reference srcml and decoded srcml:\t{round(all_srcml_edit_distance/c, 2)}') # mean edit distance
#print(f'mean edit distance between reference srcml and decoded srcml for non perfect samples only:\t{round(srcml_edit_distance_greater_than_zero/srcml_edit_distance_greater_than_zero_count, 2)}')
#print(f'median edit distance between reference srcml and decoded srcml:\t{statistics.median(srcml_levenshtein_distance_list)}')

print(f'mean length of the code in chars:\t{round(code_len / c,2 )}')
#print(f'mean length of the srcml in chars:\t{round(srcml_len / c, 2)}')

#print(f'number of perfect srcml samples\t{count_perfect_srcml}')              # number perfect (zero edit distance)

print(f'number of perfect samples:\t{p}')              # number perfect (zero edit distance)
print(f'percent of perfect samples:\t{p/(c+e1+e2)}')   # percent perfect
print(f'number of near perfect samples:\t{l}')              # number near perfect (edit distance 1-10)
print(f'percent of near perfect samples:\t{l/(c+e1+e2)}')   # percent near perfect
#print(f'number of samples without srcml prediction:\t{e1}')            # errors generating srcml (no srcml prediction)
#print(f'number of invalid srcml prediction:\t{e2}')            # errors parsing srcml (invalid srcml prediction)
#print(f'number of samples with syntax errors in reference code:\t{se}')            # number of fids with syntax errors in reference code

#def generate_histogram(data, bins):
#  plt.hist(data, bins=bins)
#  plt.xlabel('values')
#  plt.ylabel('frequency')
#  plt.title('histogram')
#  plt.show()

#toplot = list()

#for fid in results:
#  if results[fid] > 10:
#    results[fid] = 10

#  if results[fid] >= 0:
#    toplot.append(results[fid])

#generate_histogram(toplot, 10)

