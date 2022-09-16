##import libraries
import caloriecalculator.ocrtools as ocrtools

#stuff for BERT model
import pickle
import torch
import numpy as np
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import BertTokenizer, BertConfig

from keras_preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

#For parsing all useful info
import fractions

#Imports for matching with database
import json

#Based on this code, https://stackoverflow.com/questions/71828371/how-to-do-string-semantic-matching-using-gensim-in-python
from re import sub
from gensim import models
import numpy as np
from gensim.utils import simple_preprocess
import gensim.downloader as api
from gensim.corpora import Dictionary
from gensim.models import TfidfModel
from gensim.similarities import SparseTermSimilarityMatrix, WordEmbeddingSimilarityIndex, SoftCosineSimilarity
from gensim.models import KeyedVectors
from gensim.similarities import Similarity
from gensim.test.utils import common_corpus, common_dictionary, get_tmpfile
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from Levenshtein import distance as lev
import heapq

def findID(name):
    print(MatchSemantic(name, foodnames, glove_similarity_index))
    

def MatchSemantic(index, query_string, tfidf, dictionary):
    query = preprocess(query_string)
    query_tf = tfidf[dictionary.doc2bow(query)]
    return(index[query_tf])

def preprocess(doc):
    stopwords = ['the', 'and', 'are', 'a']
    # Tokenize, clean up input document string
    doc = sub(r'<img[^<>]+(>|$)', " image_token ", doc)
    doc = sub(r'<[^<>]+(>|$)', " ", doc)
    doc = sub(r'\[img_assist[^]]*?\]', " ", doc)
    doc = sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', " url_token ", doc)
    return [token for token in simple_preprocess(doc, min_len=0, max_len=float("inf")) if token not in stopwords]

class FoodDictionary:
    def __init__(self, index, foodjson, foodnames, validwords, tfidf, dictionary):
        self.index = index
        self.foodjson = foodjson
        self.foodnames = foodnames
        self.validwords = validwords
        self.tfidf = tfidf
        self.dictionary = dictionary

    def createValidQuery(self, query_string):
        #word2vec can't deal with novel queries. We use fuzzywuzzy to find the nearest match. If it is not close enough we exclude it from the query.
        qterms = query_string.split()
        moddedquery = ""
        for term in qterms:
            #find the best match for existing terms in our dictionary
            extterm = process.extractOne(term, self.validwords)
            #give a little leeway for typos but not so much we have false matches
            #print(extterm)
            if extterm[1] > 92:
                moddedquery += extterm[0]+" "
        return moddedquery                

    def search(self, query_string):
        vq = self.createValidQuery(query_string)
        if vq == "":
            return("No results found")
        #find cosine similarity scores for everything
        cossims = MatchSemantic(self.index, vq, self.tfidf)
        #find highest cosine similarity index
        resultInd = np.argmax(cossims)
        #return that index in foodnames
        return(self.foodnames[resultInd])

    def levMatch(target, array):
        #initialize to high value, pick lowest one
        lowestlev = 100000
        levindex = ""
        #calculate levensctein distance
        for i in array:
            #print(i)
            levI = lev(i, "1 "+target)
            if levI < lowestlev:
                lowestlev = levI
                levindex = i
        print("Closest unit match: {}".format(levindex))
        return levindex
        

    def calculateIngredient(self, query_string, quantity, unit):
        vq = self.createValidQuery(query_string)
        if vq == "":
            return("No results found")
        #find cosine similarity scores for everything
        cossims = MatchSemantic(self.index, vq, self.tfidf, self.dictionary)
        #find highest 20 cosine similarity indexes
        resultInds = sorted(range(len(cossims)), key=lambda i: cossims[i])[-20:]
        #multiply by log weights to determine our top search result. More common foods are more likely to be answer.
        topIndex = -1
        topScore = -1
        for resultInd in resultInds:
            #print(self.foodjson[resultInd])
            #print(cossims[resultInd])
            #multiply by logweight
            score = cossims[resultInd]* float(self.foodjson[resultInd]['softmax'])
            #print(score)
            if score > topScore:
                topIndex = resultInd
                topScore = score
        #return that index in foodnames
        result = self.foodjson[topIndex]
        #iterate through units and find closest match
        #    print(result['units'][unit])
        print(result['item_name'])
        #use levensctein distance because fuzzywuzzy is broken
        closestunit = FoodDictionary.levMatch(unit, result['units'])
        #print(result['units'][closestunit])
        unitgram = result['units'][closestunit]
        #print(unitgram)
        #print(result['kcalpergram'])
        #take grams per unit, cal per gram and quantity and multiply
        #return unitgram * quantity
        return unitgram * quantity * result['kcalpergram']

def createFoodDictionary(fpath, food2vecmodelpath):
    ##START MAIN
    foodnames = []
    foodjson = []

    ##Read in foods
    with open(fpath, "r") as f:
        j = json.load(f)
        for food in j["calorieTrackerIngredients"]:
            #print(food["name"])
            #foodnames.append(food["item_name"])
            foodjson.append(food)

    #sort by calorie count so that smallest calorie things are first
    ##Match happens on any item that matches words in document. We're going to assume that lower calorie things tend to be ingredients
    foodjson.sort(key=lambda json: json["kcalpergram"])

    for food in foodjson:
        foodnames.append(food["item_name"])



    if len(foodnames) == 1: foodnames.append('')

    # Preprocess the documents, including the query string
    #print("!!!!!!PREPROCESSING!!!!!!!!!!!")
    corpus = [preprocess(document) for document in foodnames]


    #print("!!!!!!LOADING MODEL!!!!!!!!!!!")
    # Load the model: this is a big file, can take a while to download and open.
    glove = KeyedVectors.load_word2vec_format(food2vecmodelpath)
    glove_similarity_index = WordEmbeddingSimilarityIndex(glove)

    #print("!!!!!!BUILDING DICTIONARY!!!!!!!!!!!")
    # Build the term dictionary, TF-idf model
    dictionary = Dictionary(corpus)

    #print("!!!!!!BUILDING TFIDF!!!!!!!!!!!")
    tfidf = TfidfModel(dictionary=dictionary)

    # Create the term similarity matrix.
    #print("!!!!!!CREATE SIMILARITY MATRIX!!!!!!!!!!!")
    similarity_matrix = SparseTermSimilarityMatrix(glove_similarity_index, dictionary, tfidf)
    index_tmpfile = get_tmpfile("")
    #index = Similarity(index_tmpfile, common_corpus, num_features=len(common_dictionary))  # build the index, not really clear that this does anything. It immediately gets overwritten.


    #print("!!!!!!CREATE INDEX!!!!!!!!!!!")
    index = SoftCosineSimilarity(
        tfidf[[dictionary.doc2bow(document) for document in corpus]],
        similarity_matrix)

    #print("!!!!!!CREATE DICTIONARY FOR FUZZYMATCH!!!!!!!!!!!")
    validwords = set()
    for doc in corpus:
        for word in doc:
            if word not in validwords:
                validwords.add(word)

    return FoodDictionary(index, foodjson, foodnames, validwords, tfidf, dictionary)
