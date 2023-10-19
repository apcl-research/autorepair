import pickle
import subprocess
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import javalang
import diff_match_patch as dmp_module
import statistics
srcml_dir = 'srcml_predictions'
q90codefile = '/nublar/datasets/jm52m/q90fundats-j1.pkl'
q90testfidfile = '/nublar/datasets/jm52m/q90testfids.pkl'
decoded_code_file = 'decoded_code_new.pkl'
exec(open('configurator.py').read())


q90code = pickle.load(open(q90codefile, 'rb'))
q90testfids = pickle.load(open(q90testfidfile, 'rb'))

results = dict()

for fid in tqdm(q90testfids):
  
  
    try:
        with open(f'{srcml_dir}/{fid}.xml', 'r', encoding='utf-8') as f:
            srcml_pred = f.read()
    except:
        results[fid] = 'none srcml'
        continue

    if srcml_pred == 'none':
        results[fid] = 'none srcml'
        continue

    srcml_pred = srcml_pred.strip()
    
    ref = q90code[fid]
  
    try: 
        decoded_pred = subprocess.run(['srcml', f'{srcml_dir}/{fid}.xml'], timeout=5, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8')
        results[fid] = decoded_pred
    except:
        results[fid]= "error"
        continue

    if "Error" in decoded_pred:
        results[fid]= "error"

        continue
  

pickle.dump(results, open(f'{srcml_dir}/{decoded_code_file}', 'wb'))

