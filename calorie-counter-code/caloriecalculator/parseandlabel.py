##import libraries
#import caloriecalculator.ocrtools as ocrtools
#import caloriecalculator.fooddictionary as fooddict

#stuff for BERT model
import pickle
import torch
import numpy as np
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import BertTokenizer, BertConfig

from keras_preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

import os
#For parsing all useful info
#import fractions

#Imports for matching with database
#import json


def parseandlabel(text_recipe):

    # get current directory
    path = os.getcwd()
    
    #loading model with pickle
    with open(path+"\\models\\foodbert.model", "rb") as f:
        model = torch.load(f, map_location=torch.device('cpu'))
    with open(path+"\\models\\tag_values.pickle", "rb") as f:
        tag_values = pickle.load(f)
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    #encode and pass to tokenizer for categorization
    tokenized_sentence = tokenizer.encode(text_recipe)

    #input_ids = torch.tensor([tokenized_sentence]).cuda()
    input_ids = torch.tensor([tokenized_sentence])
    with torch.no_grad():
        output = model(input_ids)
        label_indices = np.argmax(output[0].to('cpu').numpy(), axis=2)
    
    # BERT tokenizer splits tokens. We put them back together into full words
    tokens = tokenizer.convert_ids_to_tokens(input_ids.to('cpu').numpy()[0])
    new_tokens, new_labels = [], []
    for token, label_idx in zip(tokens, label_indices[0]):
        #
        if token.startswith("##"):
            new_tokens[-1] = new_tokens[-1] + token[2:]
        else:
            new_labels.append(tag_values[label_idx])
            new_tokens.append(token)

    #strip out useless O tags and fix fractions
    fin_tokens, fin_labels = [], []
    denominatorNext = False
    for t, l in zip(new_tokens, new_labels):
        if l == "O":
            pass
        elif t == "/":
            fin_tokens.append(t)
            fin_labels.append("I-qty")
            denominatorNext = True
        elif denominatorNext == True:
            fin_tokens.append(t)
            fin_labels.append("I-qty")
            denominatorNext = False
        else:
            fin_tokens.append(t)
            fin_labels.append(l)   

    

    #Combine B and I tags. This is easier to do in reverse.
    #This is because if we run into an 'I' we know there must be a 'B' later,
    #but it is difficult to say if B will be followed by I.
    fin_tokens.reverse()
    fin_labels.reverse()
    comb_tokens, comb_labels = [], []
    combtok = []
    for token, label in zip(fin_tokens, fin_labels):
        if token != "[SEP]" and token != "[CLS]":
            if label[0] == 'B':
                #combtok is backwards, we need to reverse and then combine together.
                combtok.append(token)
                combtok.reverse()
                combstr = ""
                for t in combtok:
                    combstr += t + " "
                #strip out spaces for fractions. If there are two spaces then there's a whole number we wish to keep.
                if label == "B-qty":
                    combstr = combstr.replace(" ", "")
                #append to comb tokens and labels
                comb_tokens.append(combstr)
                comb_labels.append(label)
                combtok = []
            if label[0] == 'I':
                combtok.append(token)
    comb_tokens.reverse()
    comb_labels.reverse()
    for token, label in zip(comb_tokens, comb_labels):
        print("{}\t{}".format(token, label))

    print("END PARSING")
    return comb_tokens, comb_labels
