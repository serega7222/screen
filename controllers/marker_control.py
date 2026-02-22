
#controllers/marker_control.py
from utils.log import logger
from PySide6.QtWidgets import QColorDialog                        
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from view.screen_selector import ScreenSelector
from view.paint import PainterWidget
from model.model import Model

class MarkerControl():
    """Установка цвета для ручки"""
    def __init__(self,screen:ScreenSelector,paint:PainterWidget,model:Model)-> None:
        self.screen = screen
        self.paint = paint
        self.model = model
        screen.choose_marker_signal.connect(self.open_marker)

    def open_marker(self)-> None:
        dialog = QColorDialog()
        dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        dialog.setStyleSheet("""
            QColorDialog, QWidget {
                background-color: white;
                color: black;
            }
        """)
        logger.info("Открыто окно выбора цвета")
        dialog.setCurrentColor(QColor(Qt.black))
        
        if dialog.exec():
            color = dialog.selectedColor()
            if color.isValid():
                self.color = color.name() 
                self.paint.change_marker_color(self.color)
                self.model.save_marker_color(self.color)
                self.screen.set_marker_button_color()
                logger.success(f"Выбран цвет {self.color}")
                

        else:
            logger.info("Пользователь отменил выбор цвета")        
