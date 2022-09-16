This is the code for the calorie counting application for Karl Holten.

Some dependencies are HuggingFace/BERT tokenizer, an AWS account and boto3 installed, 

OCR code to OCR directories full of images is in caloriecalculator/ocrtools.py
You may need to set up your own S3 and AWS account for OCR.

Code used to train NER model available in the bert_ner_training directory. This code ran on Google Colab.

Creating the JSON file used for the database from the FoodData Central database is available at creating-json-file.

Code to calculate calories for a recipe in calorie-counter-code/calculator_code.py
Using a knowledge base for unit matching might be a better approach to non-standard units but string match was sufficient for test data.