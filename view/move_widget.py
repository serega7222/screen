#view/move_widget.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QWidget
from PySide6.QtGui import QMouseEvent
from utils.log import logger


class MoveWidget(QCheckBox):
    """Кастомный чекбокс, который позволяет перетаскивать контейнер с инструментами.
    
    Используется в view/selector_screen.py (функция _load_screen_ui) для создания
    перетаскиваемой панели инструментов поверх скриншота.
    
    Args:
        container_to_move (QWidget): Виджет-контейнер, который будет перемещаться
            при перетаскивании этого чекбокса.
    
    Example:
        # В selector_screen.py:
        self._move_button = MoveWidget(self.tool_container)
    
    Note:
        - Перетаскивание работает только при зажатой левой кнопке мыши
        - Позиция контейнера обновляется в реальном времени
        - Логирует координаты перемещения (для отладки)
    """
    def __init__(self, container_to_move: QWidget) -> None:
        super().__init__()
        self.container_to_move = container_to_move  
        self.drag_position = None
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Запоминает начальную позицию перетаскивания.
        
        Срабатывает при нажатии левой кнопки мыши на чекбоксе.
        Вычисляет смещение между глобальной позицией курсора и позицией контейнера.
        
        Args:
            event: Событие мыши, содержит глобальные координаты курсора
        """
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.container_to_move.pos()
        
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Сбрасывает позицию перетаскивания при отпускании кнопки мыши.
        
        Args:
            event: Событие мыши (не используется, но требуется для переопределения)
        """
        self.drag_position = None
        
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Перемещает контейнер при движении мыши с зажатой кнопкой.
        
        Вычисляет новую позицию контейнера на основе текущей позиции курсора
        и сохраненного смещения. Контейнер перемещается только если:
        - Зажата левая кнопка мыши
        - Есть сохраненная позиция перетаскивания (drag_position)
        
        Args:
            event: Событие мыши с глобальными координатами курсора
        
        Note:
            Логирует новую позицию для отладки. В продакшене можно убрать
            или сделать уровень DEBUG.
        """
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.container_to_move.move(new_pos) 
            logger.info(f"Перемещение контейнера в: {new_pos.x()}, {new_pos.y()}")