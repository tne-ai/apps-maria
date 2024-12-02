import pandas as pd 

from tne.TNE import TNE
from tabulate import tabulate
import json
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


try:
    # Parse the input string as JSON
    data = json.loads(PROCESS_INPUT)
    
    # Extract chartData and tableData if they are present
    output = {}
    if "chartData" in data:
        output["chartData"] = data["chartData"]
    if "tableData" in data:
        output["tableData"] = data["tableData"]
    
    # Convert the result to a JSON string
    result = json.dumps(output, indent=4)
except Exception as e:
    # Capture the exception message in the result
    result = f"Error: {str(e)}"
