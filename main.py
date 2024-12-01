from PyQt5.QtWidgets import QApplication
from ui_loader import HeaterTestApp

if __name__ == "__main__":
    app = QApplication([])
    window = HeaterTestApp()
    window.show()
    app.exec_()
