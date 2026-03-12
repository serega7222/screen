#view/selector_screen.py
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtWidgets import QMainWindow,QRubberBand
from PySide6.QtGui import QRegion,QMouseEvent
from PySide6.QtWidgets import QMainWindow
from model.model import Model
from view.paint import PainterWidget
from view.tool_panel import ToolPanel
from utils.log import logger
from PySide6.QtWidgets import QMainWindow,QCheckBox,QMessageBox,QRubberBand,QVBoxLayout,QSlider

class ScreenSelector(QMainWindow):
    """Создает выделение"""

    def __init__(self,paint:PainterWidget,model:Model,tool_panel:ToolPanel) -> None:
        super().__init__()
        # Окно на весь экран, без рамок, поверх остальных
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.setWindowOpacity(0.6) 
        self.setWindowState(Qt.WindowFullScreen)
        self.setStyleSheet("background-color: rgba(0, 0, 0,255);") 
        self._rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self._origin = None
        self._screen_on = True
        self.step = None
        self.paint = paint
        self.model = model
        self.tool_panel = tool_panel
    def mousePressEvent(self, event : QMouseEvent)-> None:
        if self._screen_on:
            self._origin = event.pos()
            self._rubber_band.setGeometry(QRect(self._origin, QSize()))
            self._rubber_band.show()
            self._screen_on = False
        else:
            self.exit()   
            
    def mouseMoveEvent(self, event:QMouseEvent)-> None:
        if self._origin:
            self._rubber_band.setGeometry(QRect(self._origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event:QMouseEvent)-> None:
        self.selected_rect = self._rubber_band.geometry()
        self.x, self.y, self.width, self.height = self._rubber_band.geometry().getRect()
        self.x1, self.y1, self.x2, self.y2 = self.x, self.y, self.x + self.width, self.y + self.height
        self._create_selection_hole()
        self.tool_panel.load_tool_panel(self.selected_rect, )
        
    def _create_selection_hole(self) -> None:
        """Создает 'дырку' в затемненном экране  использую ее что бы показать место выделения"""
        if not self.selected_rect:
            return None
        screen_rect = self.screen().geometry()
        region = QRegion(screen_rect)
        region = region.subtracted((self.selected_rect))
        self.setMask(region) 
        self._create_paint()

    def _create_paint(self) -> None:
        """Функция которая вызывает функцию создания полотна по которому можно рисовать"""
        self.width_paint = self.selected_rect.width()
        self.height_paint =  self.selected_rect.height()
        
        self.x_paint= self.selected_rect.x()
        self.y_paint = self.selected_rect.y()        
        self.paint.create_ui(self.width_paint,self.height_paint,self.x_paint,self.y_paint)


    def exit(self) -> None:
        """Закрыть выделение и очистить всё"""
        
        # 1. Сначала скрываем резиновую ленту
        self._rubber_band.hide()
        
        # 2. Сбрасываем маску (убираем дырку)
        self.clearMask()  
        
        # 3. Возвращаем полную затемненность
        self.setStyleSheet("background-color: rgba(0, 0, 0, 255);")
        
        # 4. Сбрасываем переменные состояния
        self._origin = None
        self.selected_rect = None
        self._screen_on = True
        
        # 5. Сбрасываем геометрию резиновой ленты
        self._rubber_band.setGeometry(QRect())
        
        # 6. Закрываем дочерние элементы
        self.tool_panel.clear()
        self.paint.close_paint()
        
        # 7. Перерисовываем окно
        self.update()
        
      
        self.close() 
        
        logger.info("ScreenSelector закрыт")

    def show_popup(self, message:str)-> None:
        """Окно об ошибке"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Ошибка")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.exec()            