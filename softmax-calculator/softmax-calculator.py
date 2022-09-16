import csv
import numpy as np
import pandas as pd

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    return np.exp(x) / np.sum(np.exp(x), axis=0)

#read csv as dataframe
df = pd.read_csv("log10.csv")
#calculate softmax and assign to dataframe
sm = softmax(df['logscore'])
df = df.assign(softmax=sm)
print(df)
#fg.to_csv('test.csv')
df.to_csv('softmaxbase10.csv')
