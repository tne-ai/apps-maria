import json
# import matplotlib.pyplot as plt
from io import BytesIO
from docx import Document
from docx.shared import Inches
from tne.TNE import TNE

# Initialize the TNE object
session = TNE(uid=UID, bucket_name=BUCKET, project=PROJECT, version=VERSION)

# Load CSV content from the input
# raw_text = PROCESS_INPUT

def convert_to_docx(raw_text, table_data, chart_data, output_file):
    # Create a Word document
    doc = Document()

    # Add raw text
    doc.add_heading('Report', level=1)
    doc.add_paragraph(raw_text)

    # Parse and add table data
    '''
    doc.add_heading('Table Data', level=2)
    lines = table_data.strip().split("\n")
    headers = lines[0].split("|")[1:-1]  # Extract headers
    rows = [line.split("|")[1:-1] for line in lines[2:]]  # Extract rows

    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Table Grid'

    # Add header row
    hdr_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        hdr_cells[i].text = header.strip()

    # Add data rows
    for row in rows:
        row_cells = table.add_row().cells
        for i, cell in enumerate(row):
            row_cells[i].text = cell.strip()

    # Generate and add chart
    doc.add_heading('Chart Data', level=2)
    chart_info = json.loads(chart_data)

    plt.figure(figsize=(6, 4))
    for dataset in chart_info["data"]["datasets"]:
        plt.plot(chart_info["data"]["labels"],
                 dataset["data"],
                 label=dataset["label"],
                 color=dataset.get("borderColor", "#000"),
                 marker="o")

    plt.title(chart_info["options"]["title"]["text"])
    plt.xlabel('Year')
    plt.ylabel('Value')
    plt.grid(True)
    if chart_info["options"]["legend"]["display"]:
        plt.legend()

    # Save chart to a BytesIO buffer
    chart_stream = BytesIO()
    plt.savefig(chart_stream, format='png')
    plt.close()
    chart_stream.seek(0)

    # Insert chart image into the document
    doc.add_picture(chart_stream, width=Inches(5.5))
    chart_stream.close()

    doc.save(output_file)
    '''
    
    # Upload the document from the memory buffer
    session.upload_object(output_file, doc)
    return output_file

# Example input
# raw_text = "This report provides an overview of San Diego County's GRP from 2019 to 2023."
table_data = """| Year | GRP (Billion $) | Per Capita GRP ($) |
|------|----------------|--------------------|
| 2019 | 244.28 | 73,347 |
| 2020 | 244.82 | - |
| 2021 | 268.87 | - |
| 2022 | 296.68 | - |
| 2023 | 308.71 | 94,916 |"""
chart_data = """{
    "type": "line",
    "data": {
        "labels": ["2019", "2020", "2021", "2022", "2023"],
        "datasets": [{
            "label": "GRP (Billion $)",
            "data": [244.28, 244.82, 268.87, 296.68, 308.71],
            "borderColor": "#3e95cd",
            "fill": false
        }]
    },
    "options": {
        "title": {
            "display": true,
            "text": "San Diego County GRP 2019-2023"
        },
        "legend": {
            "display": false
        }
    }
}"""

# Output file
output_file = "SanDiego_GRP_Report.docx"

# Generate the docx file
# result = convert_to_docx(raw_text, table_data, chart_data, output_file)
raw_text = ""
for f in INPUT_FILES:
    raw_text += str(f) + "\n BREAK HERE \n \n"
result = raw_text
