import os
from fpdf import FPDF
from PyQt5.QtWidgets import QCheckBox  # Необхідно імпортувати

def generate_pdf_report(model, serial, tab_widget):
    """Генерація PDF-звіту на основі даних моделі, серійного номера та вкладок."""
    # Перевірка серійного номера
    if not serial:
        print("Помилка: Серійний номер не може бути порожнім.")
        return

    # Створення PDF
    pdf = FPDF()
    pdf.add_page()

    # Додавання шрифту Arial
    pdf.add_font('Arial', '', 'Arial.ttf', uni=True)
    pdf.set_font("Arial", size=12)

    # Додавання заголовка
    pdf.cell(200, 10, txt="Heater Test Report", ln=True, align='C')
    pdf.ln(10)

    # Додавання інформації про модель та серійний номер
    pdf.cell(200, 10, txt=f"Model: {model}", ln=True)
    pdf.cell(200, 10, txt=f"Serial: {serial}", ln=True)
    pdf.ln(10)

    # Збір даних із вкладок
    for index in range(tab_widget.count()):
        tab = tab_widget.widget(index)
        tab_name = tab_widget.tabText(index)  # Отримання назви вкладки

        # Додавання назви вкладки до PDF
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(200, 10, txt=f"Tab: {tab_name}", ln=True)
        pdf.set_font("Arial", size=12)

        # Збирання даних чекбоксів у вкладці
        checkboxes = tab.findChildren(QCheckBox)
        if checkboxes:
            for checkbox in checkboxes:
                state = "Checked" if checkbox.isChecked() else "Unchecked"
                pdf.cell(200, 10, txt=f"  {checkbox.text()}: {state}", ln=True)
        else:
            pdf.cell(200, 10, txt="  No checkboxes found.", ln=True)

        pdf.ln(5)  # Відступ між вкладками

    # Створення папки для збереження файлу, якщо її немає
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)

    # Шлях до файлу
    pdf_path = os.path.join(output_dir, f"{serial}.pdf")

    # Збереження PDF
    pdf.output(pdf_path)
    print(f"PDF збережено: {pdf_path}")
