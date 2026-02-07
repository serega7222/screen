#main.py
import sys
from PySide6.QtWidgets import QApplication
from controllers import Controller




if __name__ == "__main__":
    app = QApplication(sys.argv)
    style_file = "style.css"  # Замените на путь к вашему файлу стилей
    with open(style_file, "r",encoding="UTF-8") as file:
        app.setStyleSheet(file.read())        

    controller = Controller()
    app.setQuitOnLastWindowClosed(False)
    sys.exit(app.exec())