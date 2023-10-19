### Code for ICSE 2024 demonstration paper, A Lossless Syntax Tree Generator with Zero-shot Error Correction

Presented by:
- [Chia-Yi Su](https://chiayisu.github.io/)
- [Robert Wallace]()
- [Juliana Gonzalez]()
- [Vijayanta Jain](https://sites.google.com/maine.edu/vijayantajain/home)
- [Sepideh Ghanavati](https://www.sepidehghanavati.com)
- [Collin McMillan](https://sdf.org/~cmc/)

This repository contains all the code and detailed instructions for a tool to generate lossless syntax trees from source code using a language mode and repair syntax errors in our HuggingFace Automatic Program Comprehension Lab hub.

## To-do list
To set up your local environment, run the following command. We recommend the use of a virtual environment for running the experiments.
```
pip install -r requirements.txt
``` 

- If you want to generate the syntax trees from source code with our models, please see [Syntax Trees Generation](#syntax-tree-generation).
- If you want to finetune a model to a the syntatic bug using our processed and tokenized dataset, please see [Finetuning](#finetuning)
- If you want to recompile our datasets, please see [Dataset](#dataset)


## Syntax tree generation
After you download the dataset in our Hugginface dataset [repository](https://huggingface.co/datasets/apcl/autorepair/tree/main) and download the model file in model [repository](https://huggingface.co/apcl/autorepair/tree/main) and put the all of the files in dataset in ```/nublar/datasets/jm52m/``` and put the model file in ```jmsrcml```, you can simply run the command below to generate the syntax tree.

```
CUDA_DEVICE_ORDER='PCI_BUS_ID' CUDA_VISIBLE_DEVICES='1' OMP_NUM_THREADS=2 time torchrun --rdzv-backend=c10d --rdzv-endpoint=localhost:4111 --nnodes=1 --nproc_per_node=1  sample_srcml.py --out_dir=jmsrcml --temperature=0.001 --prediction_outdir=srcml_prediction_new --checkpoint_filename=ckpt.pt
```

```
--out_dir: directory of the model for inference
--prediction_outdir: name of the directory of the prediction file
--checkpoint_filename: the file name of the inference model
--q90codefile: file name of the function
--q90codetestfidfile: file name of the funtion id
```

## Code generation from syntax tree generation

```
python3 decoded_srcml.py 
```

```
--srcml_dir: directory of syntax tree files
--q90codefile: function files
--q90testfidfile: filename of the function id
--decoded_code_file: filename of decoded code
```

## Metrics
We provide scripts for calculating the metrics to evaluate the srcml and bug fixing rate bellow. 
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
