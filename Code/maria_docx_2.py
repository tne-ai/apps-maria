import json
from io import BytesIO
from docx import Document
from docx.shared import Inches
import matplotlib.pyplot as plt
from tne.TNE import TNE

# Initialize the TNE object
session = TNE(uid=UID, bucket_name=BUCKET, project=PROJECT, version=VERSION)

def convert_to_docx(content, output_file):
    # Create a Word document
    doc = Document()

    # Process each section in the content
    for section in content["sections"]:
        content_type = section["type"]
        content_data = section["content"]

        if content_type == "raw text":
            # Add raw text
            doc.add_paragraph(content_data)
        elif content_type == "table":
            # Parse and add table data
            doc.add_heading('Table Data', level=2)
            lines = content_data.strip().split("\n")
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
        elif content_type == "chart":
            # Generate and add chart
            doc.add_heading('Chart Data', level=2)
            chart_info = content_data

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

    # Save the document
    doc.save(output_file)

    # Upload the document to the session
    session.upload_object(output_file, doc)
    return output_file

# Load JSON content from the input
try:
    content_json = json.loads(PROCESS_INPUT)  # Parse PROCESS_INPUT string into a dictionary
    # Extract document filename and content
    output_file = content_json["document_filename"]
    content_sections = content_json
    
    # Generate the docx file
    result = convert_to_docx(content_sections, output_file)
except json.JSONDecodeError as e:
    result = f"Invalid JSON input: {e}"
