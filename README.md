# jam_dev

## Finetuning reward model
CUDA_DEVICE_ORDER='PCI_BUS_ID' CUDA_VISIBLE_DEVICES='2' OMP_NUM_THREADS=4 time torchrun --rdzv-backend=c10d --rdzv-endpoint=localhost:4333 --nnodes=1 --nproc_per_node=1 train_reward4.py config/train_reward_model.py

## Inference
CUDA_DEVICE_ORDER='PCI_BUS_ID' CUDA_VISIBLE_DEVICES='2' python3 sample_reward.py config/train_reward_model.py

## Calculate Accuracy
python3 accuracy.py

## Test data for reward model
data/cgrw/reward_test
- {function_id}_{choice (0,1,2,3)}

## Generate test data
1. python3 testidgen.py (generate function id of testset) -- already in repo (rewardtestfid.pkl)
2. python3 testdatagen.py (generate test data) -- already in repo as well
    - this will generate a directory called reward_test/ by default
