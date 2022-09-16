import json_stream
import json
import os
import csv

class Ingredient:

    def __init__(self):
        self.name = ""
        self.jsonid = -1
        self.fdcid = -1
        self.unit = []
        self.kcalpergram = -1
        
    def __str__(self):
        return "[name: "+self.name+", jsonid: "+str(self.jsonid)+", fdcid: "+str(self.fdcid)+", unit: "+str(self.unit)+"]"

    def asJson(self):
        outunit = {}
        for u in self.unit:
            outunit[u[1]] = u[0]
        return {"item_name": self.name, "jsonid": self.jsonid, "fdcid": self.fdcid, "kcalpergram": self.kcalpergram, "units": outunit}

        #this works:
        #return str([{"name": self.name}, {"jsonid": self.jsonid}, {"fdcid": self.fdcid}])

def visitorhelper(item, path):
    return visitor(item, path, ingArray, lastjsonid, lastinginfo, writecal, outfile)

def visitor(item, path, ingArray, lastjsonid, lastinginfo, writecal, outfile):
    #create a new ingredient if we finished with the last one
    if lastjsonid[0] < path[1]:
        #write old ingarray to a file
        j= ingArray[0].asJson()
        print(j)
        json.dump(j, outfile)
        outfile.write(', ')
        outfile.write('\n')
        #save id and food description to array for food2vec. Strip commas and numbers and things that cause errors
        json.dump({"item_name": ingArray[0].name, "fdcid": ingArray[0].fdcid}, idonly)
        idonly.write(', ')
        idonly.write('\n')
        #create new ingarray
        ingArray[0] = Ingredient()
        ingArray[0].jsonid = int(path[1])
        lastjsonid[0] = path[1]
        
    if (len(path) == 3):
        if path[-1] == 'description':
            #set name for ingredient
            #print("foodname: "+item)
            ingArray[0].name = item
        elif path[-1] == "fdcId":
            #print("fdcid: "+str(item))
            ingArray[0].fdcid = int(item)
    elif len(path) == 5:
        #the quantity of calories is last, so we write when we encounter it
        if path[-1] == "amount" and writecal[0]:
            writecal[0] = False
            ingArray[0].kcalpergram = item/100
            #rewriting this to be per 100 grams
            #out = [item, lastinginfo[1]]
            #out = [item/100, "gram"]
            #print(out)
            #ingArray[0].unit.append(out)
        elif path[2] == "foodPortions":
            if path[-1] == "gramWeight":
                #print("Gramweight: "+item)
                lastinginfo[0] = item
            elif path[-1] == "portionDescription":
                #print("PD: "+item)
                ingArray[0].unit.append([lastinginfo[0], item]) 
            
    elif (len(path) == 6):
        #save the name of the last nutrient we encountered. if it is not a kcal nutrient the flag to write will never get tripped.
        #if path[-1] == "name":
        #    lastinginfo[1] = item
        if item == "kcal":
            writecal[0] = True


with open("idonly.json", "w") as idonly:
    with open("processedFood.json", "w") as outfile:
        with open("D:\\cookbooks\\database\\FoodData_Central_survey_food_json_2021-10-28.json", "r") as f:

            #create containing element
            outfile.write('{"calorieTrackerIngredients": \n[')
            idonly.write('{"calorieTrackerIngredients": \n[')
            #initialize stuff to track each ingredient
            ingArray = [Ingredient()]
            lastjsonid = [-1]
            lastinginfo = [-1, "description"]
            writecal = [False]

            #create CSV writer and headers
            #csvwriter = csv.writer(csvfile, delimiter = ',')
            #csvwriter.writerow(["item_name","fdcid"])
            
            #visit each json node
            json_stream.visit(f, visitorhelper)
            #close our containing element
            outfile.write(']}')
            idonly.write(']}')

            #NOTE: after parsing manually remove the last trailing comma. 

