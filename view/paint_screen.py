#view/paint_screen.py

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter,QColor,QMouseEvent,QPaintEvent,QPen,QPixmap
from PySide6.QtWidgets import QWidget
from model import config

class PainterWidget(QWidget):
    size_pen_signal = Signal()
    """Создает прозрачное полотно по которрому можно рисовать"""
    def __init__(self,)-> None:
        super().__init__()
        self.def_size = None
        self.def_color = None
    def _create_ui(self,width:int ,height:int,pos_x:int,pos_y:int)-> None:
        """Сам процесс создания"""
        self.setFixedSize(width, height)
        self.move(pos_x,pos_y)
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(QColor(0, 0, 0, 1))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)      
        self.previous_pos = None
        self.painter = QPainter()
        self.pen = QPen()
        #посылка сигнала что экземляр создан
        self.size_pen_signal.emit()
        
        self.pen.setColor(QColor(self.def_color))
        self.pen.setWidth(self.def_size )
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)


        self.show()

    def change_color(self,color:str)-> None:
        self.pen.setColor(QColor(color))
    def load_color(self,color:str)-> None:
        self.def_color = color
    def clear_paint(self)-> None:
        self.pixmap.fill(QColor(0, 0, 0, 1))
        self.update()

    def set_size(self,size:int)-> None:
        self.pen.setWidth(size)

    def defult_size(self,size:int) -> None:
        self.def_size  = size
        
    def paintEvent(self, event: QPaintEvent)-> None:
        """Override method from QWidget

        Paint the Pixmap into the widget

        """
        with QPainter(self) as painter:
            painter.drawPixmap(0, 0, self.pixmap)

    def mousePressEvent(self, event: QMouseEvent)-> None:
        """Override from QWidget

        Called when user clicks on the mouse

        """
        self.previous_pos = event.position().toPoint()
        QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event: QMouseEvent)-> None:
        """Override method from QWidget

        Called when user moves and clicks on the mouse

        """
        current_pos = event.position().toPoint()
        self.painter.begin(self.pixmap)
        self.painter.setRenderHints(QPainter.RenderHint.Antialiasing, True)
        self.painter.setPen(self.pen)
        self.painter.drawLine(self.previous_pos, current_pos)
        self.painter.end()
        self.previous_pos = current_pos
        self.update()

        QWidget.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event: QMouseEvent)-> None:
        """Override method from QWidget

        Called when user releases the mouse

        """
        self.previous_pos = None
        QWidget.mouseReleaseEvent(self, event)

    def start_paint(self,width:int,height:int,pos_x:int,pos_y:int)-> None:
        self._create_ui(width,height,pos_x,pos_y)
