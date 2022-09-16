##import libraries
import caloriecalculator.ocrtools as ocrtools
import caloriecalculator.fooddictionary as fooddict
import caloriecalculator.parseandlabel as pnl
import caloriecalculator.queries

#for file explorer box
import tkinter as tk
from tkinter import filedialog

#ignore search warning
import warnings


def demoPrint(string, isDemo):
    if isDemo:
        print(string)
        input("Enter to continue...")

###Queries and Searching
def main():
    isDemo = False

    print("Karl Holten Thesis- Calorie Counter Workflow Demo")
    #Select picture
    root = tk.Tk()
    root.withdraw()

    document = filedialog.askopenfilename()

    demoPrint("#####BEGIN OCR#####", isDemo)
#### OCR a single image- commented out to save on AWS charges for debugging
    #document = 'recipes/berrymuffins.png'
    text_recipe = ocrtools.process_text_detection_to_string(document, "")
    print(text_recipe)

####NER Model to Extract Ingredients

    demoPrint("#####BERT LABELLING#####", isDemo)
    #BERT labelling, and data cleanup
    comb_tokens, comb_labels = pnl.parseandlabel(text_recipe)
    #Grouping together Quantities/Units/Ingredients into queries
    demoPrint("#####GROUPING LABELS INTO QUERY SETS#####", isDemo)
    queries = caloriecalculator.queries.createQueries(comb_tokens, comb_labels)
    for q in queries:
        print(q)
    #Create food dictionary object with data from JSON. Object has ability to do search
    demoPrint("#####LOAD FOOD DATABASE AND WEIGHTS#####", isDemo)
    fd = fooddict.createFoodDictionary("models/curatedProcessedFoodlog10.json", "models/food2vec.model")
    #Run queries through search
    demoPrint("#####SEARCH AND SUM CALORIES#####", isDemo)
    caloriecount = 0
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        for q in queries:
            if q.ing != "" and q.qty != "" and q.unit != "":
                print(q)
                cal_ing = fd.calculateIngredient(q.ing, q.qty, q.unit)
                print(cal_ing)
                if cal_ing != "No results found":
                    caloriecount += cal_ing
    print("Total Calories: {}".format(caloriecount))
    servings = int(input("How many servings is this recipe? "))
    print("Calories per serving: {}".format(caloriecount/servings))
    
##Execute main
if __name__ == "__main__":
    main()
