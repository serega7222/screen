#view/tool_panel.py
from PySide6.QtCore import Qt, QRect, QSize, Signal,QObject
from PySide6.QtWidgets import QMainWindow,QCheckBox,QMessageBox,QRubberBand,QVBoxLayout,QSlider
from PySide6.QtGui import QRegion,QMouseEvent
from PySide6.QtWidgets import QWidget,QMainWindow
from model.model import Model
from .move_widget import MoveWidget
from view.paint import PainterWidget
from utils.log import logger    


class ToolPanel(QObject):
    save_buffer_signal = Signal(int, int, int, int)
    save_local_signal = Signal(int, int, int, int)
    choose_pen_signal = Signal()
    choose_marker_signal = Signal()
    choose_clean_signal = Signal()
    next_signal = Signal()
    prev_signal = Signal()  
    def __init__(self,paint:PainterWidget,model:Model):
        super().__init__() 
        self.paint = paint
        self.model = model
            
    def load_tool_panel(self,selected_rect:QRect )-> None:
        """
        Загружает панель инструментов для выделенной области экрана.
        
        Args:
            selected_rect (QRect): Прямоугольник выделенной области.
                Содержит координаты и размеры области, которую выбрал пользователь.
                - x(): координата левого верхнего угла по оси X
                - y(): координата левого верхнего угла по оси Y
                - width(): ширина выделенной области
                - height(): высота выделенной области
        
        """
        self.selected_rect = selected_rect      
        # Вычисляем координаты углов
        self.x1 = selected_rect.x()                          # левый верхний X
        self.y1 = selected_rect.y()                          # левый верхний Y
        self.x2 = selected_rect.x() + selected_rect.width()  # правый нижний X
        self.y2 = selected_rect.y() + selected_rect.height() # правый нижний Y
        
        # Позиция для панели (справа от выделения)
        panel_x = self.x2  
        panel_y = self.y1
        
        self.tool_container = QWidget()  
        self.tool_container.setWindowFlags(
            Qt.FramelessWindowHint |  # Без рамки
            Qt.WindowStaysOnTopHint |  # Поверх всех окон
            Qt.Tool | # Не показывается в панели задач
            Qt.WindowDoesNotAcceptFocus#Не тераяме фокус
        )
        self.tool_container.setAttribute(Qt.WA_TranslucentBackground)  # Прозрачный фон
            
        # Создаем layout для контейнера
        layout = QVBoxLayout(self.tool_container)
        
        # Создаем кнопки с родителем tool_container
        self._move_button = MoveWidget(self.tool_container)
        self._move_button.setObjectName("move_button")
               

        self._buffer_button = QCheckBox("Buffer", self.tool_container)
        self._buffer_button.setObjectName("buffer_button")
        self._buffer_button.clicked.connect(self._click_save_buffer)
        
        self._save_button = QCheckBox("Save", self.tool_container) 
        self._save_button.clicked.connect(self._click_save_local)
        self._save_button.setObjectName("save_button")
        
        self._pen_button = QCheckBox("Pen", self.tool_container) 
        self._pen_button.clicked.connect(self._click_pen_button)
        self._pen_button.setObjectName("Pen_button")

        self._marker_button = QCheckBox("marker", self.tool_container) 
        self._marker_button.clicked.connect(self._click_marker_button)
        self._marker_button.setObjectName("marker_button")

        self._clear_button = QCheckBox("clear", self.tool_container) 
        self._clear_button .clicked.connect(self.click_clear_button)
        self._clear_button .setObjectName("clear")

        self._next_button = QCheckBox("next", self.tool_container) 
        self._next_button .clicked.connect(self._click_next_button)
        self._next_button .setObjectName("next")

        self._prev_button = QCheckBox("prev", self.tool_container) 
        self._prev_button .clicked.connect(self._click_prev_button)
        self._prev_button .setObjectName("prev")

        self._slider = QSlider(Qt.Vertical)
        self._load_step()
        self._slider.setRange(0, 100) # Диапазон от 0 до 100
        self._slider.setValue(self.step)     # Начальное значение
        self._slider.valueChanged.connect(self._slider_update)
        # Добавляем в layout
        layout.addWidget(self._move_button)
        layout.addWidget(self._buffer_button)
        layout.addWidget(self._save_button)
        layout.addWidget(self._pen_button)
        layout.addWidget(self._marker_button)
        layout.addWidget(self._next_button)
        layout.addWidget(self._prev_button)
        layout.addWidget(self._clear_button )
        layout.addWidget(self._slider)
        
        layout.addStretch()
        self.set_pen_button_color()
        self.set_marker_button_color()
        self.tool_container.move(panel_x, panel_y)
        self.tool_container.show()


        
        #self.exit_signal.emit()
        
    def clear(self)-> None:
        """Очищает полотно и удаляет кнопки"""
        #удаление кнопко
        button = ['_buffer_button','_save_button',
                  '_pen_button','_clear_button',
                  '_slider','_move_button',"_marker_button","_next_button","_prev_button"]
        
        # Удаляем через цикл
        for name in button:
            if hasattr(self, name):
                getattr(self, name).deleteLater()
                delattr(self, name)      

  

    def show_popup(self, message:str)-> None:
        """Окно об ошибке"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Ошибка")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.exec()     

    def _click_save_buffer(self)-> None:
        logger.info("Сохранить в буффер")
        self.save_buffer_signal.emit(self.x1, self.y1, self.x2, self.y2)

    def _click_save_local(self) -> None:
        logger.info("Сохранить на пк")
        self.save_local_signal.emit(self.x1, self.y1, self.x2, self.y2)
    
    def _click_pen_button(self) -> None:
        logger.info("Выбрана ручка")
        self.choose_pen_signal.emit()

    def _click_marker_button(self) -> None:
        logger.info("Выбран маркер")
        self.choose_marker_signal.emit()
    
    def  click_clear_button (self)-> None:
        logger.info("Выбрана отчистка полотна")
        self.choose_clean_signal.emit()

    def set_pen_button_color(self)-> None:    
        color = self.model.load_color()
        self._pen_button.setStyleSheet(f"background-color : {color}")
        self._pen_button.update()

    def set_marker_button_color(self)-> None:    
        marker_color = self.model.load_marker_color()
        self._marker_button.setStyleSheet(f"background-color : {marker_color}")

    def _slider_update(self,value)-> None:  
        self.model.save_pen_size(value)
        self.paint.set_pen_size(value)

    def _load_step(self)-> None:  
        self.step = self.model.load_pen_size()
        self.paint.set_pen_size(self.step)

    def _click_next_button(self)-> None:  
        self.next_signal.emit()
        logger.info("Шаг вперед")    

    def _click_prev_button(self)-> None:  
        self.prev_signal.emit()
        logger.info("Шаг назад")         