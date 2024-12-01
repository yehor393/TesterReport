from PyQt5.QtWidgets import QMainWindow, QLineEdit, QCheckBox, QTabWidget, QPushButton
from PyQt5.uic import loadUi
from pdf_generator import generate_pdf_report
from set_tabs import set_tabs_for_model

class HeaterTestApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Завантаження UI
        loadUi("frontend.ui", self)


        # Отримання доступу до елементів інтерфейсу
        self.tab_widget: QTabWidget = self.findChild(QTabWidget, "tabWidget")
        self.model_input: QLineEdit = self.findChild(QLineEdit, "model_input")  # Поле моделі
        self.serial_input: QLineEdit = self.findChild(QLineEdit, "serial_input")  # Поле серійного номера
        self.checkbox_list = self.findChildren(QCheckBox)
        self.post_button: QPushButton = self.findChild(QPushButton, "post_button")  # Кнопка для створення PDF
        self.clear_button: QPushButton = self.findChild(QPushButton, "clear_button")  # Кнопка для очищення
        self.fill_button: QPushButton = self.findChild(QPushButton, "fill_button")

        # Підключення кнопок до функцій
        self.clear_button.clicked.connect(self.clear_all_fields)
        self.fill_button.clicked.connect(self.clear_all_fields)
        self.post_button.clicked.connect(self.generate_pdf)


        # Отримуємо доступ до вкладок (QTabWidget) та поля введення (QLineEdit)
        self.tab_widget: QTabWidget = self.findChild(QTabWidget, "tabWidget")  # Замініть "tabWidget" на ім'я вашого QTabWidget
        self.model_input: QLineEdit = self.findChild(QLineEdit, "line_model")  # Замініть "modelInput" на ім'я вашого QLineEdit

        # Підключаємо подію введення тексту
        self.model_input.editingFinished.connect(self.on_model_entered)

        # Зберігаємо вкладки як окремі віджети
        self.outside_steam = self.tab_widget.widget(0)
        self.outside_convector = self.tab_widget.widget(1)
        self.value = self.tab_widget.widget(2)
        self.final = self.tab_widget.widget(3)

        # Видаляємо всі вкладки на старті
        self.clear_tabs()


    def generate_pdf(self):
        """Збір даних та виклик функції створення PDF."""
        # Збір даних
        model = self.model_input.text()
        serial = self.serial_input.text()
        checkbox_results = [f"Checkbox {i+1}: {'Checked' if checkbox.isChecked() else 'Unchecked'}"
                            for i, checkbox in enumerate(self.checkbox_list)]

        # Виклик функції для створення PDF
        generate_pdf_report(model, serial, checkbox_results)

    def clear_tabs(self):
        """Видаляє всі вкладки."""
        while self.tab_widget.count() > 0:
            self.tab_widget.removeTab(0)

    def on_model_entered(self):
        """Обробляємо подію після введення моделі."""
        model = self.model_input.text().strip()  # Отримуємо текст із поля введення

        if model:  # Перевіряємо, чи введено модель
            self.set_tabs_for_model(model)

    def clear_all_fields(self):
        # Очищення чекбоксів
        for checkbox in self.checkbox_list:
            checkbox.setChecked(False)

    def fill_all_fields(self):
        # Заповнення чекбоксів
        for checkbox in self.checkbox_list:
            checkbox.setChecked(True)
