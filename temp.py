from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton
import sys

class TestApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Основне вікно
        self.setWindowTitle("Test Heater Application")
        self.setGeometry(100, 100, 800, 600)

        # Головний віджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Поле для моделі
        self.model_input = QLineEdit(self)
        self.model_input.setPlaceholderText("Enter Model")
        self.model_input.setGeometry(20, 20, 200, 30)

        # Кнопка для підтвердження
        self.submit_button = QPushButton("Apply Model", self)
        self.submit_button.setGeometry(240, 20, 100, 30)
        self.submit_button.clicked.connect(self.update_tabs)

        # Таб віджет
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setGeometry(20, 70, 760, 500)

        # Початкові вкладки
        self.update_tabs()

    def update_tabs(self):
        # Видаляємо всі існуючі вкладки
        self.tab_widget.clear()

        # Отримуємо текст моделі
        model = self.model_input.text()

        # Додаємо вкладки залежно від моделі
        if model.startswith("CX1-"):
            self.add_test_tab("Voltage Test")
            self.add_test_tab("Amperage Test")
        elif model.startswith("FX6-"):
            self.add_test_tab("Dielectric Test")
            self.add_test_tab("Temperature Test")
        else:
            self.add_test_tab("General Test")

    def add_test_tab(self, tab_name):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Perform {tab_name} here"))
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, tab_name)

# Запуск програми
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestApp()
    window.show()
    sys.exit(app.exec_())
