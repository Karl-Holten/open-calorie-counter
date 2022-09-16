#For parsing all useful info
import fractions

#Imports for matching with database
import json

###Queries and Searching

class CalorieQuery:
    def __init__(self):
        self.qty = 0
        self.unit = ""
        self.ing = ""

    def __str__(self):
        return "ING: "+self.ing+" | QTY: "+str(self.qty)+" | UNIT: "+self.unit

    def setQty(self, qty):
        #handle numeric quantities first
        if qty.isdigit():
            self.qty = float(qty)
        #handle numbers written as strings
        elif qty.find("/") != -1:
            fract = qty.partition("/")
            #print(fract)
            #if numerator is greater than denominator, it's a mixed fraction. We split the numerator into whole part and numerator part.
            if int(fract[0]) > int(fract[2]):
                self.qty = float(fract[0][0]) + (float(fract[0][1])/float(fract[2]))                
            #if numerator is less than denominator it's just a fraction
            else:
                self.qty = float(fractions.Fraction(qty))

    def setIng(self, ing):
        self.ing = ing
    def setUnit(self, unit):
        self.unit = unit
    def setCont(self, cont):
        self.ing = cont
        self.unit = cont
    def setUnquant(self, nqt):
        self.ing = nqt
        #default unit exists, use it when not quantified amount
        self.unit = "Quantity not specified"
        self.qty = 1
    def addQty(self, qty):
        #handle numeric quantities first
        if qty.isdigit():
            self.qty += float(qty)
        #handle numbers written as strings
        elif qty.find("/") != -1:
            self.qty += float(fractions.Fraction(qty))
    def addIng(self, ing):
        self.ing += " " + ing
    def addUnit(self, unit):
        self.unit += " "+ unit
    def addCont(self, cont):
        self.ing = " "+ cont
        self.unit = " "+ cont
    def addUnquant(self, nqt):
        self.ing += " "+ nqt

    def clone(self):
        clone = CalorieQuery()
        clone.ing = self.ing
        clone.unit = self.unit
        clone.qty = self.qty
        return clone

def createQueries(comb_tokens, comb_labels):
    prevlabel = ""
    prevtoken = ""
    queries = []
    afterOr = False
    
    for token, label in zip(comb_tokens, comb_labels):
        ##Logic to group together queries        
        ##We skip information after an "or" unless it is 
        if afterOr:
            #if immediately after the or, we skip no matter what
            if prevtoken == "or":
                pass
            #if not the first entry after an or, then a new query starts with a new qty or nqt.
            elif label == "B-qty" or label == "B-nqt":
                afterOr = False
                
        if afterOr == False and label != "O" and label != "":
            #print("{}\t{}".format(label, token))
            if label == "B-qty":
                if prevlabel == "B-func":
                    pass
                else:
                    queries.append(CalorieQuery())
                queries[-1].setQty(token)
            elif label == "I-qty":
                queries[-1].addQty(token)
            elif label == "B-ing":
                queries[-1].setIng(token)
            elif label == "I-ing":
                queries[-1].addIng(token)
            elif label == "B-unit":
                queries[-1].setUnit(token)
            elif label == "I-unit":
                queries[-1].addUnit(token)
            elif label == "B-cont":
                queries[-1].setCont(token)
            elif label == "I-cont":
                queries[-1].addCont(token)
            elif label == "B-nqt":
                if prevlabel == "B-func":
                    pass
                else:
                    queries.append(CalorieQuery())
                queries[-1].setUnquant(token)
            elif label == "I-nqt":
                queries[-1].addUnquant(token)
            elif label == "B-func": 
                if token == "and":
                    #And means that elements such as qty or unit have been copied from the previous entry. Duplicate that entry.
                    nq = queries[-1].clone()
                    queries.append(nq)
                elif token == "or":
                    #OR means that we ignore whatever comes after the or until we reach a point where we can start a new entry
                    afterOr = True
        #save prev label/token
        prevlabel = label
        prevtoken = token
    return queries    
