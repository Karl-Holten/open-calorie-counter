This code takes an image of a recipe and converts it into a calorie count for the recipe.

Some dependencies are HuggingFace/BERT tokenizer, an AWS account and boto3 installed. 
Full dependencies are in /calorie-counter-code/requirements.txt

Code to calculate calories for a recipe in calorie-counter-code/calculator_code.py

Using a knowledge base for unit matching might be a better approach to non-standard units and abbreviations,
but string match was sufficient for test data.

Additional helper code to train models and create knowledge base is located in the other folders.
OCR code to OCR directories full of images is in caloriecalculator/ocrtools.py. You may need to set up your own S3 and AWS account for OCR.
Code used to train NER model available in the bert_ner_training directory. This code originally ran on Google Colab.
Creating the JSON file used for the database from the FoodData Central database is available at creating-json-file.