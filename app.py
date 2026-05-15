from flask import Flask, render_template, request, send_file
import json
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import PageBreak
from reportlab.lib.pagesizes import letter
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():

    with open("components.json", "r") as file:
        components = json.load(file)

    return render_template("index.html", components=components)


@app.route("/generate_pdf", methods=["POST"])
def generate_pdf():

    bom_data = request.json

    pdf_file = "BOM_Report.pdf"

    doc = SimpleDocTemplate(pdf_file, pagesize=letter)

    elements = []

    styles = getSampleStyleSheet()

    title = Paragraph("BOM Cost Report", styles['Title'])

    elements.append(title)

    date = Paragraph(
        f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        styles['Normal']
    )

    elements.append(date)

    elements.append(Spacer(1, 20))

    table_data = [
        ["Component", "Unit Price", "Quantity", "Total"]
    ]

    grand_total = 0

    for item in bom_data:

        row_total = item["unit_price"] * item["quantity"]

        grand_total += row_total

        table_data.append([
            item["name"],
            f"₹{item['unit_price']}",
            item["quantity"],
            f"₹{row_total}"
        ])

    gst = grand_total * 0.18

    final_total = grand_total + gst

    table_data.append(["", "", "Subtotal", f"₹{grand_total}"])

    table_data.append(["", "", "GST (18%)", f"₹{gst:.2f}"])

    table_data.append(["", "", "Final Total", f"₹{final_total:.2f}"])

    table = Table(table_data)

    table.setStyle(TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),

        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('GRID', (0, 0), (-1, -1), 1, colors.black),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

    ]))

    elements.append(table)

    doc.build(elements)

    return send_file(pdf_file, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)