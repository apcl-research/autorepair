import time

#out_dir = 'out-owt-gpt2mini'
out_dir = 'out-funcom_raw_scratch'
eval_interval = 1000
eval_iters = 40

wandb_log = True # feel free to turn on
wandb_project = 'fundats_srcml'
wandb_run_name = 'ft-gpt2-srcml-1' #+ str(time.time())

dataset = 'pretrain'
init_from = 'scratch'
#init_from = 'gpt2-large'

# only save checkpoints if the validation loss improves
always_save_checkpoint = True

#n_layer = 6
#n_head = 6
#n_embd = 384
#dropout = 0.2

block_size = 1024

# gpt2-large
#n_layer = 36
#n_head = 20
#n_embd = 1280
#dropout = 0.2

# gpt2-medium
n_layer = 24
n_head = 16
n_embd = 1024
#dropout = 0.2

# the number of examples per iter:
# 1 batch_size * 32 grad_accum * 1024 tokens = 32,768 tokens/iter
# shakespeare has 301,966 tokens, so 1 epoch ~= 9.2 iters

# stackoverflow has 10,495,518,108 tokens
# openwebtext has 9,035,582,489 tokens
# funcom_raw has 8,752,695,577 tokens

# fundats_srcml has 48,774,749,459 tokens

batch_size = 4
gradient_accumulation_steps = 32
max_iters = 1200000

# finetune at constant LR
learning_rate = 3e-5
decay_lr = False

#weight_decay = 1e-1
