"""
Sample from a trained model
"""
import os
import pickle
from contextlib import nullcontext
import torch
import tiktoken
from model import GPTConfig, GPT
import re
import tqdm
import random

# -----------------------------------------------------------------------------
init_from = 'resume' # either 'resume' (from an out_dir) or a gpt2 variant (e.g. 'gpt2-xl')
out_dir = 'jmsrcml' # ignored if init_from is not 'resume'
start = "\n" # or "<|endoftext|>" or etc. Can also specify a file, use as: "FILE:prompt.txt"
num_samples = 1 # number of samples to draw
max_new_tokens = 1024 # number of tokens generated in each sample
temperature = 0.001 # 1.0 = no change, < 1.0 = less random, > 1.0 = more random, in predictions
top_k = 200 # retain only the top_k most likely tokens, clamp others to have 0 probability
seed = 1337
device = 'cuda' # examples: 'cpu', 'cuda', 'cuda:0', 'cuda:1', etc.
dtype = 'bfloat16' # 'float32' or 'bfloat16' or 'float16'
use_srcml = False
checkpoint_filename ='ckpt.pt'
prediction_outdir = 'srcml_bug'
compile = False # use PyTorch 2.0 to compile the model to be faster
exec(open('configurator.py').read()) # overrides from command line or config file
# -----------------------------------------------------------------------------

torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
torch.backends.cuda.matmul.allow_tf32 = True # allow tf32 on matmul
torch.backends.cudnn.allow_tf32 = True # allow tf32 on cudnn
device_type = 'cuda' if 'cuda' in device else 'cpu' # for later use in torch.autocast
ptdtype = {'float32': torch.float32, 'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
ctx = nullcontext() if device_type == 'cpu' else torch.amp.autocast(device_type=device_type, dtype=ptdtype)

pred_file = f'predict_{out_dir}.txt'

if(not os.path.exists(prediction_outdir)):
    os.mkdir(prediction_outdir)
#if(not os.path.exists('funcom_predictions')):
#    os.mkdir('funcom_predictions')

# model
if init_from == 'resume':
    # init from a model saved in a specific directory
    ckpt_path = os.path.join(out_dir, checkpoint_filename)
    checkpoint = torch.load(ckpt_path, map_location=device)
    gptconf = GPTConfig(**checkpoint['model_args'])
    model = GPT(gptconf)
    state_dict = checkpoint['model']
    unwanted_prefix = '_orig_mod.'
    for k,v in list(state_dict.items()):
        if k.startswith(unwanted_prefix):
            state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)
    model.load_state_dict(state_dict)
elif init_from.startswith('gpt2'):
    # init from a given GPT-2 model
    model = GPT.from_pretrained(init_from, dict(dropout=0.0))

model.eval()
model.to(device)
if compile:
    model = torch.compile(model) # requires PyTorch 2.0 (optional)

# look for the meta pickle in case it is available in the dataset folder
load_meta = False
if init_from == 'resume' and 'config' in checkpoint and 'dataset' in checkpoint['config']: # older checkpoints might not have these...
    meta_path = os.path.join('data', checkpoint['config']['dataset'], 'meta.pkl')
    load_meta = os.path.exists(meta_path)
if load_meta:
    print(f"Loading meta from {meta_path}...")
    with open(meta_path, 'rb') as f:
        meta = pickle.load(f)
    # TODO want to make this more general to arbitrary encoder/decoder schemes
    stoi, itos = meta['stoi'], meta['itos']
    encode = lambda s: [stoi[c] for c in s]
    decode = lambda l: ''.join([itos[i] for i in l])
else:
    # ok let's assume gpt-2 encodings by default
    print("No meta.pkl found, assuming GPT-2 encodings...")
    enc = tiktoken.get_encoding("gpt2")
    encode = lambda s: enc.encode(s, allowed_special={"<|endoftext|>"})
    decode = lambda l: enc.decode(l)

#srcml = pickle.load(open('/nublar/datasets/jm52m/q90testfids_srcml.pkl', 'rb'))

q90code = pickle.load(open('/nublar/datasets/jm52m/q90fundats-j1.pkl', 'rb'))
q90_bug_code = pickle.load(open('./data/autorepair/test_bug_code.pkl', 'rb'))
q90testfids = pickle.load(open('/nublar/datasets/jm52m/q90testfids.pkl', 'rb'))

#srcmldir = 'srcml_prediction_bug_new'
#arr = os.listdir(srcml)
#testfiles = []
#for file in arr:
#    if file.endswith('.txt'):
#        testfiles.append(testdir + file)

#pf = dict() #= open(f'srcml_predictions/{pred_file}', 'w')

#c = 0

for fid in tqdm.tqdm(q90testfids):
    code = q90_bug_code[fid]['bug_code']
    start = f'TDAT: {code}\nSRCMLAST:'

    start_ids = encode(start)
    x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...])

    # run generation
    with torch.no_grad():
        with ctx:
            for k in range(num_samples):
                try:
                    y = model.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)
                    ret = decode(y[0].tolist())
                    ret = ret.replace('\n', '<NLSPECIAL>')
                    ret = re.search('SRCMLAST:(.*)<\|endoftext\|>', ret, re.MULTILINE)
                    ret = ret.group(1)
                    ret = ret.replace('<NLSPECIAL>', '\n')
                    ret = ret[:ret.find('<|endoftext|>')]
                    ret = ret.strip()
                    ret = f'{ret}\n'
                    pf = ret
                except:
                    pf = 'none'
                outf = open(f'{prediction_outdir}/{fid}.xml', 'w')
                
                outf.write(pf)
                outf.flush()
                outf.close()




