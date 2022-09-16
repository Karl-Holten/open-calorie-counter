#Detects text in a document stored in an S3 bucket. Display polygon box around text and angled text 
import boto3
import io
from io import BytesIO
import sys
import os
import psutil
import time
import re
import math
from PIL import Image, ImageDraw, ImageFont
import csv

###stuff for BERT model
##import pickle
##import torch
##import numpy as np
##from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
##from transformers import BertTokenizer, BertConfig
##
##from keras_preprocessing.sequence import pad_sequences
##from sklearn.model_selection import train_test_split
##
###For parsing all useful info
##import fractions
##
###Imports for matching with database
##import json
##
###Based on this code, https://stackoverflow.com/questions/71828371/how-to-do-string-semantic-matching-using-gensim-in-python
##from re import sub
##from gensim import models
##import numpy as np
##from gensim.utils import simple_preprocess
##import gensim.downloader as api
##from gensim.corpora import Dictionary
##from gensim.models import TfidfModel
##from gensim.similarities import SparseTermSimilarityMatrix, WordEmbeddingSimilarityIndex, SoftCosineSimilarity
##from gensim.models import KeyedVectors
##from gensim.similarities import Similarity
##from gensim.test.utils import common_corpus, common_dictionary, get_tmpfile
##from fuzzywuzzy import process
##import heapq




#def findID(name):
#    print(MatchSemantic(name, foodnames, glove_similarity_index))
    

###OCR COMPONENT STUFF
# From amazon, Displays information about a block returned by text detection and text analysis
def DisplayBlockInformation(block):
    print('Id: {}'.format(block['Id']))
    if 'Text' in block:
        print(block['Text'])
        print('    Detected: ' + block['Text'])
    print('    Type: ' + block['BlockType'])
   
    if 'Confidence' in block:
        print('    Confidence: ' + "{:.2f}".format(block['Confidence']) + "%")

    if block['BlockType'] == 'CELL':
        print("    Cell information")
        print("        Column: " + str(block['ColumnIndex']))
        print("        Row: " + str(block['RowIndex']))
        print("        ColumnSpan: " + str(block['ColumnSpan']))
        print("        RowSpan: " + str(block['RowSpan']))    
    
    if 'Relationships' in block:
        print('    Relationships: {}'.format(block['Relationships']))
    print('    Geometry: ')
    print('        Bounding Box: {}'.format(block['Geometry']['BoundingBox']))
    print('        Polygon: {}'.format(block['Geometry']['Polygon']))
    
    if block['BlockType'] == "KEY_VALUE_SET":
        print ('    Entity Type: ' + block['EntityTypes'][0])
    if 'Page' in block:
        print('Page: ' + block['Page'])
    print()

##find and replace all super and subscripts with just the number  
def errorCorrect(s):
    s = s.replace("⁰", "0")
    s = s.replace("₀", "0")
    s = s.replace("¹", "1")
    s = s.replace("₁", "1")
    s = s.replace("²", "2")
    s = s.replace("₂", "2")
    s = s.replace("³", "3")
    s = s.replace("₃", "3")
    s = s.replace("⁴", "4")
    s = s.replace("₄", "4")
    s = s.replace("⁵", "5")
    s = s.replace("₅", "5")
    s = s.replace("⁶", "6")
    s = s.replace("₆", "6")
    s = s.replace("⁷", "7")
    s = s.replace("₇", "7")
    s = s.replace("⁸", "8")
    s = s.replace("₈", "8")
    s = s.replace("⁹", "9")
    s = s.replace("₉", "9")
    #first person pronoun much less likely than a misread number in a recipe
    s = s.replace("I ", "1 ")
    s = s.replace("I/", "1/")
    
    #regex to seperate numerator from whole number
    s = re.sub(r'([0-9])([0-9])(?=\/)', '\g<1> \g<2>', s)
    return(s)

def process_text_detection_to_file(document, out):
    # Open using aws client for detecting text in the document
    client = boto3.client('textract')
    #open 
    with open(document, "rb") as doc:
        stream = io.BytesIO(doc.read())
        image=Image.open(stream)
        image_binary = stream.getvalue()
        response = client.detect_document_text(Document={'Bytes': image_binary})

        #Get the text blocks
        blocks=response['Blocks']
        print ('Detected Document Text')
       
        # Create image showing bounding box/polygon the detected lines/text
        lastrow = -1
        for block in blocks:
            if block['BlockType'] == 'LINE': 
                    #error correction fixes super/subscripts and inserts spaces between whole number and start of fraction
                    correctedText = errorCorrect(block['Text'])    
                    #print(correctedText)
                    out.write(correctedText)
                    out.write('\n')
        return blocks

def process_text_detection_to_string(document, out):
    # Open using aws client for detecting text in the document
    client = boto3.client('textract')
    #open 
    with open(document, "rb") as doc:
        stream = io.BytesIO(doc.read())
        image=Image.open(stream)
        image_binary = stream.getvalue()
        response = client.detect_document_text(Document={'Bytes': image_binary})

        #Get the text blocks
        blocks=response['Blocks']
        #return blocks
        #for block in blocks:
        #    DisplayBlockInformation(block)
        print ('Detected Document Text')
       
        # Create image showing bounding box/polygon the detected lines/text
        lastrow = -1
        for block in blocks:
            if block['BlockType'] == 'LINE': 
                    #error correction fixes super/subscripts and inserts spaces between whole number and start of fraction
                    correctedText = errorCorrect(block['Text'])    
                    #print(correctedText)
                    out += correctedText
                    out += '\n'
        return out


def traverseAndOCR(traindir):
    for a, b, c in os.walk(traindir):
        #define outfile name
        ofname = a+'\\'+'000_ocr.txt'
        with open(ofname, "w") as outfile:
            #print("With outfile created, run OCR on the following........")
            for png in c:
                pngpath = str(a+'\\'+png)
                print("Processing: "+pngpath)
                process_text_detection_to_file(pngpath, outfile)

