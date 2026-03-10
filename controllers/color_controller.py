#controllers/color_controller.py
from utils.log import logger
from PySide6.QtWidgets import QColorDialog                        
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from view.screen_selector import ScreenSelector
from view.paint import PainterWidget
from model.model import Model

class PenOrMarker():
    MARKER = "marker"
    PEN = "pen"

class ColorPickerController():
    """Открывает диалоговое окно,устанавливает цвет маркера и ручки 
    ,устанавливает цвет заднего фона"""
    def __init__(self,screen:ScreenSelector,paint:PainterWidget,model:Model)-> None:
        self.screen = screen
        self.paint = paint
        self.model = model        
        self._connect_signals()

    def _connect_signals(self):
        # Используем lambda для передачи аргумента
        self.screen.choose_pen_signal.connect(
            lambda: self._open_color_picker(PenOrMarker.PEN)
        )
        self.screen.choose_marker_signal.connect(
            lambda: self._open_color_picker(PenOrMarker.MARKER)
        )

    def _open_color_picker(self,mode)-> None:
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
                color = color.name() 
                if mode == "pen":
                    self.paint.change_color_pen(color)
                    self.model.save_color(color)
                    self.screen.set_pen_button_color()
                    logger.success(f"Выбран цвет {color}")    

                if mode == "marker" :
                    self.paint.change_marker_color(color)
                    self.model.save_marker_color(color)
                    self.screen.set_marker_button_color()
                    logger.success(f"Выбран цвет {color}")                                       

        else:
            logger.info("Пользователь отменил выбор цвета")    
