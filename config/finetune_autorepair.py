import time

#out_dir = 'out-owt-gpt2mini'
out_dir = 'out-autorepair'
eval_interval = 100
eval_iters = 80
wandb_log = True
wandb_project = 'autorepair'
wandb_run_name = 'autorepair'

dataset = 'autorepair'
init_from = 'resume'

# only save checkpoints if the validation loss improves
always_save_checkpoint = False

#n_layer = 24
#n_head = 16
#n_embd = 1024
#dropout = 0.2

# the number of examples per iter:
# 1 batch_size * 32 grad_accum * 1024 tokens = 32,768 tokens/iter
# shakespeare has 301,966 tokens, so 1 epoch ~= 9.2 iters

# autorepair finetuned has 39,413,485 tokens
# jam 1024 has 127,000 iters
# jam-srcml has 570,000 iters
block_size = 1024

batch_size = 4 #16
gradient_accumulation_steps = 32
#max_iters = 5600 # 172394 training samples

max_iters = 570000 + 305 * 3

# finetune at constant LR
learning_rate = 3e-5
decay_lr = False
