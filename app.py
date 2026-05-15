from flask import Flask, render_template, request, send_file, jsonify
import json
import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():

    with open("components.json", "r") as file:
        components = json.load(file)

    saved_files = os.listdir("saved_boms")

    return render_template(
        "index.html",
        components=components,
        saved_files=saved_files
    )


@app.route("/generate_pdf", methods=["POST"])
def generate_pdf():

    bom_data = request.json

    pdf_file = "BOM_Report.pdf"

    doc = SimpleDocTemplate(pdf_file, pagesize=letter)

    elements = []

    styles = getSampleStyleSheet()

    title = Paragraph("BOM Cost Report", styles['Title'])

    elements.append(title)

    elements.append(Spacer(1, 20))

    table_data = [["Component", "Unit Price", "Qty", "Total"]]

    grand_total = 0

    for item in bom_data:

        total = item["unit_price"] * item["quantity"]

        grand_total += total

        table_data.append([
            item["name"],
            f"₹{item['unit_price']}",
            item["quantity"],
            f"₹{total}"
        ])

    gst = grand_total * 0.18

    final_total = grand_total + gst

    table_data.append(["", "", "Subtotal", f"₹{grand_total}"])
    table_data.append(["", "", "GST", f"₹{gst:.2f}"])
    table_data.append(["", "", "Final", f"₹{final_total:.2f}"])

    table = Table(table_data)

    table.setStyle(TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),

        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('GRID', (0, 0), (-1, -1), 1, colors.black)

    ]))

    elements.append(table)

    doc.build(elements)

    return send_file(pdf_file, as_attachment=True)


@app.route("/save_bom", methods=["POST"])
def save_bom():

    data = request.json

    project_name = data["project_name"]

    bom_items = data["bom_items"]

    file_path = f"saved_boms/{project_name}.json"

    with open(file_path, "w") as file:

        json.dump(bom_items, file, indent=4)

    return jsonify({"message": "Saved Successfully"})


@app.route("/load_bom/<filename>")
def load_bom(filename):

    file_path = f"saved_boms/{filename}"

    with open(file_path, "r") as file:

        data = json.load(file)

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)