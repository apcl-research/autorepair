### Code for A Trainable Lossless Syntax Tree Generator

Presented by:
- [Chia-Yi Su](https://chiayisu.github.io/)
- [Robert Wallace]()
- [Juliana Gonzalez]()
- [Vijayanta Jain](https://sites.google.com/maine.edu/vijayantajain/home)
- [Sepideh Ghanavati](https://www.sepidehghanavati.com)
- [Collin McMillan](https://sdf.org/~cmc/)

This repository contains all the code and detailed instructions for a tool to generate lossless syntax trees from source code using a language mode and repair syntax errors in our HuggingFace Automatic Program Comprehension Lab hub.

## Quick link
- [To-do list](#to-do-list)
- [Error Correction in Zero-Shot Setting](#error-correction-in-zero-shot-setting)
- [Finetuning](#finetuning)
- [Metrics](#metrics)
- [Dataset](#dataset)
- [Retrain from scratch](#retrain-from-scratch)

## To-do list
To set up your local environment, run the following command. We recommend the use of a virtual environment for running the experiments.
```
pip install -r requirements.txt
``` 

- If you want to generate the syntax trees from source code or correct syntactic eorrs in zero-shot setting with our models, please see [Error Correction in Zero-Shot Setting](#error-correction-in-zero-shot-setting).
- If you want to finetune a model to fix the syntactic bug using our processed and tokenized dataset, please see [Finetuning](#finetuning)
- If you want to retrain the model from scratch, please see [Retrain from scratch](#retrain-from-scratch)


## Error Correction in Zero-Shot Setting

### Step 1: Download dataset and models
Please downlaod the ``fundats.tar.gz`` file in our Hugginface dataset [repo](https://huggingface.co/datasets/apcl/autorepair/tree/main) and download the ``ckpt_base.pt`` file in the model [repo](https://huggingface.co/apcl/autorepair/tree/main) and place all of the files in ``fundats.tar.gz`` in ```/nublar/datasets/jm52m/``` and palce the model file in ```jmsrcml```

### Step 2: Syntax tree generation

```
CUDA_DEVICE_ORDER='PCI_BUS_ID' CUDA_VISIBLE_DEVICES='1' OMP_NUM_THREADS=2 time torchrun --rdzv-backend=c10d --rdzv-endpoint=localhost:4111 --nnodes=1 --nproc_per_node=1  sample_srcml.py --out_dir=jmsrcml --temperature=0.001 --prediction_outdir=srcml_prediction_new --checkpoint_filename=ckpt_base.pt
```

```
--out_dir: directory of the model for inference
--prediction_outdir: name of the directory of the prediction file
--checkpoint_filename: the filename of the inference model
--q90codefile: filename of the function
--q90codetestfidfile: filename of the funtion id
```
### Step 3: Code generation from syntax tree
```
python3 decoded_srcml.py 
```

```
--srcml_dir: directory of syntax tree files
--q90codefile: function files
--q90testfidfile: filename of the function id
--decoded_code_file: filename of decoded code
```

## Finetuning
These steps will show you how to fine-tune the model to fix the syntax errors and make the inference by using the model that you finetune

### Step 1: Download the finetuning dataset
Please download ```bin.tar.gz``` in our Hugginface [repo](https://huggingface.co/datasets/apcl/autorepair/tree/main) and put ```train.bin``` and ```val.bin``` to the same dir as ```--dataset``` in ```config/finetune_autorepair.py```, which is ```data/autorepair``` for now.

### Step 2: Download the models for finetuning
Please download the checkpoint files named ```ckpt.pt``` in our Hugginface [repo](https://huggingface.co/apcl/autorepair/tree/main) for finetuning and put the checkpoint to the same dir as ```--out_dir``` in ```config/finetune_autorepair.py```.

### Step 3: Finetuning model
```
CUDA_DEVICE_ORDER='PCI_BUS_ID' CUDA_VISIBLE_DEVICES='0' OMP_NUM_THREADS=2 time torchrun --rdzv-backend=c10d --rdzv-endpoint=localhost:4000 --nnodes=1 --nproc_per_node=1  train.py config/finetune_autorepair.py --outfilename=ckpt.pt
```

### Step 4: Inference
```
CUDA_DEVICE_ORDER='PCI_BUS_ID' CUDA_VISIBLE_DEVICES='0' OMP_NUM_THREADS=2 time torchrun --rdzv-backend=c10d --rdzv-endpoint=localhost:4000 --nnodes=1 --nproc_per_node=1 sample_autorepair.py config/finetune_autorepair.py --prediction_filename=predict_autorepair_srcml.pkl --outfilename=ckpt.pt
```

## Metrics
We provide scripts for calculating the metrics to evaluate the srcml and bug fixing rate bellow. 

### Merics for evaluating syntax tree
```
python3 eval_srcml.py
```
```
--srcml_dir: syntax tree prediction directory
--q90codefile: function file
--q90testsrcmlfile: reference syntax tree file
--q90testfidsfile: function id file
--q90decodedcodefile: decoded code file
```

### Merics for evaluatig finetuning bug fixing rate

```
python3 autorepair_base_fix_rate.py
```
```
--reference_code_file: filename of the reference code
--prediction_file: filename of the prediction code
```

### Merics for evaluatig zero-shot bug fixing rate
```
python3 srcml_bug_fix_rate.py
```
```
srcml_dir: directory of syntax tree files
q90testfidsfile: filename of funtion id
bug_code_file: filename of the funtions with syntax errors
q90codefile: filename of reference code
```

## Dataset 

We also release all of our raw datasets for finetuning in our Hugginface [repo](https://huggingface.co/datasets/apcl/autorepair/tree/main) and the scripts for compiling the raw data to ``bin`` files in this Github repo. Before running the command, please create three dir: ``pkls``, ``bins``, and ``tmp``. Then, you can simply run the following command to generate ``train.bin`` and ``val.bin``.

```
python3 data/autorepair/prepare_fc_raw.py
```

```
--q90trainfids-file: filename of training function id
--q90testfids-file: filename of test function id
--q90valfids-file: filename of val function id
--fundats-file: filename of function
--train-fundats-file: filename for the function with the syntax error for training
--val-fundats-file: filename for the function with the syntax error for val
```

## Retrain from scratch
### Step 1: Download the dataset
Please download ``train.bin.gz`` and ``val.bin.gz`` in our Hugginface [repo](https://huggingface.co/datasets/apcl/autorepair/tree/main) and extract and put those files to the same dir as ```--dataset``` in ```config/pretraining.py```, which is ```data/pretrain``` for now.
### Step 2: Retrain model
```
CUDA_DEVICE_ORDER='PCI_BUS_ID' CUDA_VISIBLE_DEVICES='0' OMP_NUM_THREADS=2 time torchrun --rdzv-backend=c10d --rdzv-endpoint=localhost:4000 --nnodes=1 --nproc_per_node=1  train.py config/pretraining.py 
```
