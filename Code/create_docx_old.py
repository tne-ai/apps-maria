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

    # -- 1. Set up header and footer (if provided) --
    #    By default, .sections[0] is the first (and often only) section.
    section = doc.sections[0]
    if "header_text" in content:
        header = section.header
        header_paragraph = header.paragraphs[0]
        header_paragraph.text = content["header_text"]

    if "footer_text" in content:
        footer = section.footer
        footer_paragraph = footer.paragraphs[0]
        footer_paragraph.text = content["footer_text"]

    # -- 2. Add a main title to the document (if provided) --
    if "doc_title" in content:
        doc.add_heading(content["doc_title"], level=0)

    # -- 3. Process each section in the content --
    for section_data in content["sections"]:
        content_type = section_data["type"]
        content_text = section_data["content"]

        # (A) Optionally add a heading for this section
        if "heading" in section_data:
            # You can choose the heading level (1, 2, 3, etc.) 
            # or base it on the JSON input.
            doc.add_heading(section_data["heading"], level=2)

        # (B) Check the content type and handle accordingly
        if content_type == "raw text":
            # Add raw text with a specific style (optional)
            paragraph = doc.add_paragraph(content_text)
            if "style" in section_data:
                paragraph.style = section_data["style"]

        elif content_type == "table":
            # Convert text into table rows
            lines = content_text.strip().split("\n")
            headers = lines[0].split("|")  # Extract headers
            rows = [line.split("|") for line in lines[1:]]  # Extract rows

            table = doc.add_table(rows=1, cols=len(headers))
            table.style = 'Table Grid'

            # (i) Add header row
            hdr_cells = table.rows[0].cells
            for i, header_text in enumerate(headers):
                hdr_cells[i].text = header_text.strip()

            # (ii) Add data rows
            for row_data in rows:
                row_cells = table.add_row().cells
                for i, cell_data in enumerate(row_data):
                    row_cells[i].text = cell_data.strip()

            # (iii) Add caption if present
            if "caption" in section_data:
                caption_para = doc.add_paragraph(section_data["caption"])
                caption_para.style = "Caption"  # You can define a custom style

        elif content_type == "chart":
            # Parse chart data, generate a chart with matplotlib, then insert it
            try:
                chart_info = json.loads(content_text)

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

                # Add caption if present
                if "caption" in section_data:
                    caption_para = doc.add_paragraph(section_data["caption"])
                    caption_para.style = "Caption"

            except Exception as e:
                # You might want to log the error
                print(f"Error parsing chart data: {e}")
                continue

    # -- 4. Save and upload the document --
    doc.save(output_file)
    session.upload_object(output_file, doc)
    return output_file

# Load JSON content from the input
try:
    content_json = json.loads(PROCESS_INPUT)  # Parse PROCESS_INPUT string into a dictionary
    # Extract document filename
    output_file = content_json["document_filename"]

    # Generate the docx file
    result = convert_to_docx(content_json, output_file)
except json.JSONDecodeError as e:
    result = f"Invalid JSON input: {e}"
