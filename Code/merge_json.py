import pandas as pd 

from tne.TNE import TNE
from tabulate import tabulate
import json

session = TNE(uid=UID, bucket_name=BUCKET, project=PROJECT, version=VERSION)
json_string = session.get_object('sec1_json.txt')

document_filename = PROCESS_INPUT
try:
    # Parse the input string as JSON
    data = json.loads(json_string)
    
    data['document_link_text'] = document_filename
    
    # Convert the result to a JSON string
    result = json.dumps(data, indent=4)
except Exception as e:
    # Capture the exception message in the result
    result = f"Error: {str(e)}"
