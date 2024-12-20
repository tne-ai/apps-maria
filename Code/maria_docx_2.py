import json
from io import BytesIO
from docx import Document
from docx.shared import Inches
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from tne.TNE import TNE

# Initialize the TNE object
session = TNE(uid=UID, bucket_name=BUCKET, project=PROJECT, version=VERSION)

def currency_formatter(value, pos):
    # Format the number with commas and prepend a dollar sign
    return '${:,.2f}'.format(value)

def comma_formatter(value, pos):
    # Format the number with commas only
    return '{:,.0f}'.format(value)

def parse_chart_data(content_data):
    """
    Attempt to parse the chart data which may sometimes be double-encoded or contain additional formatting.
    We try multiple attempts to decode JSON content.
    """
    try:
        # First try to load as is
        return json.loads(content_data)
    except json.JSONDecodeError:
        # If that fails, sometimes the data might be JSON within a string
        # Try loading twice
        try:
            return json.loads(json.loads(content_data))
        except:
            # If still failing, return None or raise
            return None

def format_axis_ticks(ax, callback):
    """
    Apply formatting to the axis ticks based on the callback string.
    We look for patterns in the callback function. For example:
    - "return '$' + value.toLocaleString();" means currency formatting
    - "return value.toLocaleString();" means comma formatting
    """
    if callback and "toLocaleString" in callback:
        if "$" in callback:
            ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
        else:
            ax.yaxis.set_major_formatter(FuncFormatter(comma_formatter))
    else:
        # Default formatting if no recognizable callback
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:,.0f}"))

def convert_to_docx(content, output_file):
    # Create a Word document
    doc = Document()
    doc.add_heading('Report', level=1)

    # Process each section in the content
    for section in content["sections"]:
        content_type = section["type"]
        content_data = section["content"]

        if content_type == "raw text":
            # Add raw text
            doc.add_paragraph(content_data)

        elif content_type == "table":
            # Parse and add table data
            lines = content_data.strip().split("\n")
            headers = lines[0].split("|")  # Extract headers
            rows = [line.split("|") for line in lines[1:]]  # Extract rows

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
            # Enhanced chart rendering with flexibility and multiple attempts to parse data
            chart_info = parse_chart_data(content_data)
            if chart_info is None:
                # If we still can't parse, skip this chart
                continue

            try:
                chart_type = chart_info.get("type", "line")
                data = chart_info.get("data", {})
                options = chart_info.get("options", {})

                labels = data.get("labels", [])
                datasets = data.get("datasets", [])

                fig, ax = plt.subplots(figsize=(6,4))

                # Handle scales (yAxes)
                y_axes_config = options.get("scales", {}).get("yAxes", [])
                axis_map = {}

                # Primary Y-axis
                if y_axes_config:
                    primary_yaxis_conf = y_axes_config[0]
                    axis_map[primary_yaxis_conf.get("id", "y-axis-0")] = ax

                    # Additional Y-axes
                    for extra_yaxis_conf in y_axes_config[1:]:
                        twin_ax = ax.twinx()
                        # For multiple secondary y-axes, more complex positioning may be needed.
                        axis_map[extra_yaxis_conf.get("id", "y-axis-1")] = twin_ax
                else:
                    # No yAxes config, single default axis
                    axis_map["y-axis-0"] = ax

                # Set Y-axis labels and formatting
                for yaxis_conf in y_axes_config:
                    y_id = yaxis_conf.get("id", "y-axis-0")
                    current_ax = axis_map[y_id]

                    # Axis label
                    scale_label = yaxis_conf.get("scaleLabel", {})
                    if scale_label.get("display", False):
                        current_ax.set_ylabel(scale_label.get("labelString", ""), fontsize=10)

                    # Tick formatting
                    ticks_conf = yaxis_conf.get("ticks", {})
                    callback = ticks_conf.get("callback", "")
                    format_axis_ticks(current_ax, callback)

                # If no yAxes config at all, set a default formatter
                if not y_axes_config:
                    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:,.0f}"))

                # X-axis label if provided
                x_axes_config = options.get("scales", {}).get("xAxes", [])
                if x_axes_config:
                    x_axis_conf = x_axes_config[0]
                    scale_label = x_axis_conf.get("scaleLabel", {})
                    if scale_label.get("display", False):
                        ax.set_xlabel(scale_label.get("labelString", ""), fontsize=10)
                else:
                    ax.set_xlabel('Year')

                # Plot datasets
                for dataset in datasets:
                    yAxisID = dataset.get("yAxisID", "y-axis-0")
                    plot_ax = axis_map.get(yAxisID, ax)

                    color = dataset.get("borderColor", "#000")
                    label = dataset.get("label", "")
                    line_data = dataset.get("data", [])

                    if chart_type == "line":
                        plot_ax.plot(labels, line_data, label=label, color=color, marker="o")
                    elif chart_type == "bar":
                        # Basic bar plotting (may need adjustments for grouped bars)
                        plot_ax.bar(labels, line_data, label=label, color=color)
                    else:
                        # Fallback to line plot if type not recognized
                        plot_ax.plot(labels, line_data, label=label, color=color, marker="o")

                # Title
                title_conf = options.get("title", {})
                if title_conf.get("display", False):
                    plt.title(title_conf.get("text", ""), fontsize=12)

                # Grid
                ax.grid(True)

                # Legend
                legend_conf = options.get("legend", {})
                # Default True if not specified
                if legend_conf.get("display", True):
                    # Combine legends from all axes
                    handles, labels_legend = [], []
                    for axis_id, axis_obj in axis_map.items():
                        h, l = axis_obj.get_legend_handles_labels()
                        handles.extend(h)
                        labels_legend.extend(l)
                    if handles:
                        ax.legend(handles, labels_legend, loc='best')

                # Save chart to a BytesIO buffer
                chart_stream = BytesIO()
                plt.savefig(chart_stream, format='png')
                plt.close(fig)
                chart_stream.seek(0)

                # Insert chart image into the document
                doc.add_picture(chart_stream, width=Inches(5.5))
                chart_stream.close()

            except:
                # If something fails, skip
                continue

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
