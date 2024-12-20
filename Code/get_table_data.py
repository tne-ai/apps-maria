import json

try:
    # Parse the input string as JSON
    data = json.loads(PROCESS_INPUT)
    
    # Extract tableData if they are present
    output = {}
    if "tableData" in data:
        output["tableData"] = data["tableData"]
    
    # Convert the result to a JSON string
    result = json.dumps(output, indent=4)
except Exception as e:
    # Capture the exception message in the result
    result = f"Error: {str(e)}"
