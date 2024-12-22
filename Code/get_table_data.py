import json
from tne.TNE import TNE

try:
    # Parse the input string as JSON
    # for f in INPUT_FILES:
    #     session = TNE(uid=UID, bucket_name=BUCKET, project=PROJECT, version=VERSION)
    #     data = session.get_object(f)
    #     data = json.loads(data)
    
    #     # Extract tableData if they are present
    #     output = {}
    #     if "tableData" in data:
    #         output["tableData"] = data["tableData"]
    
    #     # Convert the result to a JSON string
    #     result = json.dumps(output, indent=4)
    
    session = TNE(uid=UID, bucket_name=BUCKET, project=PROJECT, version=VERSION)
    data = session.get_object("final_json_no_chart.txt")
    data = json.loads(data)

    # Extract tableData if they are present
    output = {}
    if "tableData" in data:
        output["tableData"] = data["tableData"]

    # Convert the result to a JSON string
    result = json.dumps(output, indent=4)
except Exception as e:
    # Capture the exception message in the result
    result = f"Error: {str(e)}"
