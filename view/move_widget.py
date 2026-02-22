#view/move_widget.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget

class MoveWidget(QCheckBox):
    """Создает виджет который можно двигать ,в нашел случае чекбокс"""
    def __init__(self, container_to_move :QWidget, parent=None) -> None:
        super().__init__(parent)
        self.container_to_move = container_to_move  
        self.drag_position = None
    
    def mousePressEvent(self, event:QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            
            self.drag_position = event.globalPosition().toPoint() - self.container_to_move.pos()
           
        
    def mouseReleaseEvent(self, event:QMouseEvent) -> None:
        self.drag_position = None
        
        
    def mouseMoveEvent(self, event:QMouseEvent) -> None:
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.container_to_move.move(new_pos) 
            print(f"Перемещение контейнера в: {new_pos.x()}, {new_pos.y()}")