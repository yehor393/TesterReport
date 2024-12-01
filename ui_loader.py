from PyQt5.QtWidgets import QMainWindow, QLineEdit, QCheckBox, QTabWidget, QPushButton
from PyQt5.uic import loadUi
from pdf_generator import generate_pdf_report

class HeaterTestApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Завантаження UI
        loadUi("frontend.ui", self)


        # Отримання доступу до елементів інтерфейсу
        self.tab_widget: QTabWidget = self.findChild(QTabWidget, "tabWidget")

        self.serial_input: QLineEdit = self.findChild(QLineEdit, "serial_input")  # Поле серійного номера
        self.model_input: QLineEdit = self.findChild(QLineEdit, "line_model")  # Замініть "modelInput" на ім'я вашого QLineEdit

        self.post_button: QPushButton = self.findChild(QPushButton, "post_button")  # Кнопка для створення PDF

        # Підключення кнопок до функцій
        self.post_button.clicked.connect(self.generate_pdf)

        # Підключаємо подію введення тексту
        self.model_input.editingFinished.connect(self.on_model_entered)

        # Зберігаємо вкладки як окремі віджети
        self.outside_steam = self.tab_widget.widget(0)
        self.outside_convector = self.tab_widget.widget(1)
        self.value = self.tab_widget.widget(2)
        self.final = self.tab_widget.widget(3)

        # Видаляємо всі вкладки на старті
        self.clear_tabs()


    def on_model_entered(self):
        """Обробляємо подію після введення моделі."""
        model = self.model_input.text().strip()  # Отримуємо текст із поля введення

        if model:  # Перевіряємо, чи введено модель
            self.set_tabs_for_model(model)
        else:  # Якщо поле порожнє
            self.clear_tabs() 


    def set_tabs_for_model(self, model):
        """Додає потрібні вкладки залежно від моделі."""
        self.clear_all_checkboxes()
        self.clear_tabs()
        if model == "FX6":
            self.tab_widget.addTab(self.outside_steam, "Outside")
            self.tab_widget.addTab(self.value, "Value")
            self.tab_widget.addTab(self.final, "Final")
        elif model == "CX1":
            self.tab_widget.addTab(self.outside_convector, "Outside")
            self.tab_widget.addTab(self.value, "Value")
            self.tab_widget.addTab(self.final, "Final")
        else:
            self.clear_tabs()
            
        self.initialize_active_tab()


    def initialize_active_tab(self):
        """Ініціалізація всіх вкладок після введення моделі."""
        self.checkbox_lists = {}  # Словник для чекбоксів кожної вкладки

        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)
            
            # Знаходимо чекбокси тільки у поточній вкладці
            self.checkbox_lists[index] = tab.findChildren(QCheckBox)

            # Знайти всі кнопки на вкладці
            buttons = tab.findChildren(QPushButton)

            # Обробити кнопки за іменами
            for button in buttons:
                    
                    try:
                        button.clicked.disconnect()
                    except TypeError:
                        pass
                    
                    if "clear_button" in button.objectName():
                        button.clicked.connect(lambda _, b=button: self.clear_fields(b))
                    elif "fill_button" in button.objectName():
                        button.clicked.connect(lambda _, b=button: self.fill_fields(b))

    def clear_all_checkboxes(self):
        """Очищує всі чекбокси на всіх вкладках."""
        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)
            checkboxes = tab.findChildren(QCheckBox)
            for checkbox in checkboxes:
                checkbox.setChecked(False)
                
    def clear_fields(self, button):
        """Очищення полів, пов'язаних із кнопкою."""
        tab = self.get_parent_tab(button)  # Отримуємо вкладку
        if tab:  # Перевіряємо, чи вкладка знайдена
            checkboxes = tab.findChildren(QCheckBox)  # Знаходимо чекбокси у вкладці
            for checkbox in checkboxes:
                checkbox.setChecked(False)


    def fill_fields(self, button):
        """Заповнення полів, пов'язаних із кнопкою."""
        tab = self.get_parent_tab(button)  # Отримуємо вкладку
        if tab:  # Перевіряємо, чи вкладка знайдена
            checkboxes = tab.findChildren(QCheckBox)  # Знаходимо чекбокси у вкладці
            for checkbox in checkboxes:
                checkbox.setChecked(True)
            # Повернути фокус на кнопку
        button.setFocus()

    def get_parent_tab(self, widget):
        """Отримати вкладку, якій належить віджет."""
        while widget and widget not in [self.tab_widget.widget(i) for i in range(self.tab_widget.count())]:
            widget = widget.parent()
        return widget
    

    def clear_all_fields(self, index):
        """Очищення чекбоксів у заданій вкладці."""
        for checkbox in self.checkbox_lists.get(index, []):
            checkbox.setChecked(False)


    def fill_all_fields(self, index):
        """Заповнення чекбоксів у заданій вкладці."""
        for checkbox in self.checkbox_lists.get(index, []):
            checkbox.setChecked(True)


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