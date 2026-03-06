#view/paint_screen.py

from PySide6.QtCore import Qt, Signal,QPoint
from PySide6.QtGui import QPainter,QColor,QMouseEvent,QPaintEvent,QPen,QPixmap,QPolygon
from PySide6.QtWidgets import QWidget
from model.model import config
from model.model import Model

class PainterWidget(QWidget):
    pen_move_signal = Signal(object,object,object,int,int)
    pen_is_up_signal = Signal()
    clear_lst_signal = Signal()
    """Создает прозрачное полотно по которрому можно рисовать"""
    def __init__(self,model:Model)-> None:
        super().__init__()
        self.model = model
        self.points = QPolygon()
        
    def create_ui(self,width:int ,height:int,pos_x:int,pos_y:int)-> None:
        """Сам процесс создания"""
        self.setFixedSize(width, height)
        self.move(pos_x,pos_y)
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(QColor(0, 0, 0, 1))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.CustomizeWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)      
        self.previous_pos = None
        self.painter = QPainter()
        self.pen = QPen()
        self._load_defalt_color()
        self.pen.setWidth(10)



        self.show()

 
        
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
        self.current_pos = event.position().toPoint()
        color = self.pen.color()
        width = self.pen.width()
        alpha = color.alpha()
       
        self.pen_move_signal.emit(self.current_pos,self.previous_pos,color,width,alpha)
        
        #self.draw()
        QWidget.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event: QMouseEvent)-> None:
        """Override method from QWidget

        Called when user releases the mouse

        """
        self.previous_pos = None
        self.pen_is_up_signal.emit()
        QWidget.mouseReleaseEvent(self, event)
        self.points.clear()

    def close_paint(self)-> None:  
        self.clear_lst_signal.emit()
        return super().close()
    
    def _load_defalt_color(self)-> None:  
       x = self.model.load_color()
       self.pen.setColor(x)    

    def change_color_pen(self,color)-> None:  
        self.pen.setColor(color)
        
    def set_pen_size(self,value)-> None:  
        self.pen.setWidth(value)

    def change_marker_color(self,color)-> None:  
        
        self.qcolor = QColor(color)
        self.qcolor.setAlpha(50)  # Устанавливаем прозрачность здесь
        self.pen.setColor( self.qcolor)     

    def clear_paint(self)-> None: 
        self.pixmap.fill(QColor(0, 0, 0, 1))
        self.update()

    def draw(self, lines: list) -> None:
        self.painter.begin(self.pixmap)
        self.painter.setRenderHints(QPainter.RenderHint.Antialiasing, True)
        self.painter.setPen(self.pen)        
        self.painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)

        for start, end, color,width,alpha in lines:
            
            qcolor = QColor(color)
            # Устанавливаем прозрачность
            qcolor.setAlpha(alpha)
            # Создаем перо
            self.pen = QPen(qcolor, width)
            self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            self.pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            
            self.painter.setPen(self.pen)
            self.points.append(QPoint(start))  # Первая точка
            self.points.append(QPoint(end))# Вторая точка
        
        
            self.painter.drawPolyline(self.points)
            self.points.clear()
        self.painter.end()
        self.previous_pos = self.current_pos
        self.update()


