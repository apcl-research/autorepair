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


## Syntax Tree Generation
