#from transformers import BertTokenizer
import re
from nltk.tokenize import word_tokenize, sent_tokenize


def qtyCounter(tokens, regExp):
    qtyCt = 0
    for tok in tokens:
        if re.search(regExp,tok) is not None:
            qtyCt += 1
    return qtyCt

def regexBioTagger(prevtok, curtok, regExp, label):
    #if curtok doesn't match, curtok is O
    if re.search(regExp,curtok) is None:
        return "O"
    else:
        #if curtok matches and prevtok doesn't, curtok is B
        if re.search(regExp,prevtok) is None:
            return "B-"+label
        #if both curtok and prevtok match, curtok is I
        else:
            return "I-"+label

def matchBioTagger(prevtok, curtok, matches, label):
    if curtok in matches:
        #if both in matches, curtok is I
        if prevtok in matches:
            return "I-"+label
        #if prevtok not in matches and curtok is, curtok is B
        else:
            return "B-"+label
    #if curtok doesn't match, curtok is O
    else:
        return "O"
        
#instantiate tokenizer for BERT- use full words since all tutorials expect it
#tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

#read in unitTokens
unitTokens = []
with open("units.txt", "rt") as infile:
    lines = infile.readlines()
    for line in lines:
        tokens = word_tokenize(line)
        for tok in tokens:
            unitTokens.append(tok)

#read in ingredientTokens
ingTokens = []
with open("ingredients.txt", "rt") as infile:
    lines = infile.readlines()
    for line in lines:
        tokens = word_tokenize(line)
        for tok in tokens:
            ingTokens.append(tok)

#read in countableTokens
countTokens = []
with open("countable.txt", "rt") as infile:
    lines = infile.readlines()
    for line in lines:
        tokens = word_tokenize(line)
        for tok in tokens:
            countTokens.append(tok)

#read in spiceTokens
spiceTokens = []
with open("spices.txt", "rt") as infile:
    lines = infile.readlines()
    for line in lines:
        tokens = word_tokenize(line)
        for tok in tokens:
            spiceTokens.append(tok)
            

#read in functionTokens
functionTokens = []
with open("functions.txt", "rt") as infile:
    lines = infile.readlines()
    for line in lines:
        tokens = word_tokenize(line)
        for tok in tokens:
            functionTokens.append(tok)
            

#read in file, tokenize line by line, write each to an outfile.
with open("parsed.txt", "wt") as outfile:
    #write headers row
    headers = "Sentence #,Word,Tag"
    outfile.writelines(headers)
    print(headers)
    with open("allrecipes.txt", "rt") as infile:    
        #use NLTK tokenizer for sentences
        sentences = sent_tokenize(infile.read())
        #each new line is a new sentence
        sentNum = 0
        for sent in sentences:
            #increment sentence number
            sentNum += 1
            #tokenize as words
            tokens = word_tokenize(sent)

            #count if there are multiple quantities, if there 3+ we declare this is a ingredients section
            qtyct = qtyCounter(tokens, "[0-9\/]")
            if qtyct > 2:
                tagSent = True
            else:
                tagSent = False

            if tagSent:
                #need dummy value since we need to know prevtok when we do BIO tagging
                prevtok = "DUMMYTOK"
                for curtok in tokens:
                    #ignore all commas because they're our delimiter and don't really matter
                    if curtok != ",":
                        #calculate unitTag and qtyTag
                        unitTag = matchBioTagger(prevtok, curtok, unitTokens, "unit")
                        qtyTag = regexBioTagger(prevtok, curtok, "[0-9\/]", "qty")
                        ingTag = matchBioTagger(prevtok, curtok, ingTokens, "ing")
                        spiceTag = matchBioTagger(prevtok, curtok, spiceTokens, "spic")
                        countTag = matchBioTagger(prevtok, curtok, countTokens, "cont")
                        functTag = matchBioTagger(prevtok, curtok, functionTokens, "func")
                        #write whatever tag is valid 
                        if unitTag == "B-unit" or unitTag == "I-unit":
                            outtag = unitTag
                        elif qtyTag == "B-qty" or qtyTag == "I-qty":
                            outtag = qtyTag
                        elif ingTag == "B-ing" or ingTag == "I-ing":
                            outtag = ingTag
                        elif spiceTag == "B-spic" or spiceTag == "I-spic":
                            outtag = spiceTag
                        elif countTag == "B-cont" or countTag == "I-cont":
                            outtag = countTag
                        elif functTag == "B-func" or functTag == "I-func":
                            outtag = functTag
                        else:
                            outtag = "O"
                        lineout ="Sentence: "+str(sentNum)+","+curtok+","+outtag
                        #print(lineout)
                        outfile.writelines(lineout+'\n')
                        #prepare for next token
                        prevtok = curtok
            else:
                for curtok in tokens:
                    if curtok != ",":
                        lineout ="Sentence: "+str(sentNum)+","+curtok+",O"
                        outfile.writelines(lineout+'\n')
                        #prepare for next token
                        prevtok = curtok
