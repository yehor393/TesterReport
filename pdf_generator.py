from fpdf import FPDF

def generate_pdf_report(model, serial, checkbox_results):
    """Генерація PDF-звіту на основі зібраних даних."""
    # Створення PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Додавання тексту до PDF
    pdf.cell(200, 10, txt="Heater Test Report", ln=True, align='C')
    pdf.ln(10)  # Додати відступ
    pdf.cell(200, 10, txt=f"Model: {model}", ln=True)
    pdf.cell(200, 10, txt=f"Serial: {serial}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt="Checkbox Results:", ln=True)
    for result in checkbox_results:
        pdf.cell(200, 10, txt=result, ln=True)

    # Збереження PDF
    pdf_path = "resources/heater_test_report.pdf"
    pdf.output(pdf_path)
    print(f"PDF збережено: {pdf_path}")
