#view/selector_screen.py
from PySide6.QtCore import Qt, QRect, QSize, Signal
from PySide6.QtWidgets import QMainWindow,QCheckBox,QMessageBox,QRubberBand,QVBoxLayout,QSlider
from PySide6.QtGui import QRegion,QMouseEvent
from PySide6.QtWidgets import QWidget,QMainWindow
from model.model import Model
from .move_widget import MoveWidget
from view.paint import PainterWidget
from utils.log import logger

class ScreenSelector(QMainWindow):
    """Создает выделение"""
    save_buffer_signal = Signal(int, int, int, int)
    save_local_signal = Signal(int, int, int, int)
    choose_pen_signal = Signal()
    choose_marker_signal = Signal()
    choose_clean_signal = Signal()
    next_signal = Signal()
    prev_signal = Signal()
    exit_signal = Signal()
    def __init__(self,paint:PainterWidget,model:Model) -> None:
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
    def mousePressEvent(self, event : QMouseEvent)-> None:
        if self._screen_on:
            self._origin = event.pos()
            self._rubber_band.setGeometry(QRect(self._origin, QSize()))
            self._rubber_band.show()
            self._screen_on = False
        else:
            self._exit()   
            
    def mouseMoveEvent(self, event:QMouseEvent)-> None:
        if self._origin:
            self._rubber_band.setGeometry(QRect(self._origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event:QMouseEvent)-> None:
        self.selected_rect = self._rubber_band.geometry()
        self.x, self.y, self.width, self.height = self._rubber_band.geometry().getRect()
        self.x1, self.y1, self.x2, self.y2 = self.x, self.y, self.x + self.width, self.y + self.height
        self._create_selection_hole()
        self._load_screen_ui()
        
    def _create_selection_hole(self) -> None:
        """Создает 'дырку' в затемненном экране"""
        if not self.selected_rect:
            return None
        screen_rect = self.screen().geometry()
        region = QRegion(screen_rect)
        region = region.subtracted((self.selected_rect))
        self.setMask(region) 
        self._create_paint()

    def _create_paint(self) -> None:
        """Функция которая вызывает функцию созадния полотна"""
        self.width_paint = self.selected_rect.width()
        self.height_paint =  self.selected_rect.height()
        
        self.x_paint= self.selected_rect.x()
        self.y_paint = self.selected_rect.y()        
        self.paint.create_ui(self.width_paint,self.height_paint,self.x_paint,self.y_paint)


    def _load_screen_ui(self)-> None:
        """Создает панель инстументов"""
        # Получаем координаты справа от выделенной области
        x = self.selected_rect.x() + self.selected_rect.width()
        y = self.selected_rect.y()
        
        # Создаем контейнер как отдельное окно (без родителя)
        self.tool_container = QWidget()  # Убираем self из параметров!
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
        self._move_button = MoveWidget(self.tool_container,self.tool_container)
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
        self.tool_container.show()

    def _exit(self)-> None:
        self._rubber_band.hide()
        self._clear()
        self.close() # Закрыть окно после выбора
        self.paint.close_paint()
        
        #self.exit_signal.emit()
        
    def _clear(self)-> None:
        """Очищает выделение и сбрасывает состояние"""
        #удаление кнопко
        button = ['_buffer_button','_save_button',
                  '_pen_button','_clear_button',
                  '_slider','_move_button',"_marker_button","_next_button","_prev_button"]
        
        # Удаляем через цикл
        for name in button:
            if hasattr(self, name):
                getattr(self, name).deleteLater()
                delattr(self, name)      

        # Скрываем резиновую ленту
        self._rubber_band.hide()
        # Сбрасываем переменные состояния
        self._origin = None
        self.selected_rect = None
        self._screen_on = True
        # Убираем маску окна (если была установлена)
        self.clearMask()
        # Сбрасываем геометрию резиновой ленты
        self._rubber_band.setGeometry(QRect())
        # Перерисовываем окно
        self.update()
        # Возвращаем полностью затемненный экран
        self.setStyleSheet("background-color: rgba(0, 0, 0, 255);")         

    def show_popup(self, message:str)-> None:
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