import pandas as pd 

from tne.TNE import TNE
from tabulate import tabulate
'''
if type(PROCESS_INPUT) is pd.DataFrame:
    if PROCESS_INPUT.empty:
        result = "<EMPTY DATAFRAME>"
    else:
        result = tabulate(PROCESS_INPUT, 
                          headers="keys", 
                          tablefmt="pipe", 
                          showindex=False)
elif type(PROCESS_INPUT) is str:
    result = PROCESS_INPUT 
else:
    result = "<ERROR>" 
'''
result = "hello"
