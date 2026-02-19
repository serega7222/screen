#view/selector_screen.py
from PySide6.QtCore import Qt, QRect, QSize, Signal
from PySide6.QtWidgets import QMainWindow,QCheckBox,QMessageBox,QRubberBand,QVBoxLayout,QSlider
from PySide6.QtGui import QRegion,QMouseEvent
from PySide6.QtWidgets import QWidget,QMainWindow

class MoveWidget(QCheckBox):
    """Создает виджет который можно двигать ,в нашел случае чекбокс"""
    def __init__(self, container_to_move :QWidget, parent=None) -> None:
        super().__init__(parent)
        self.container_to_move = container_to_move  # Сохраняем ссылку на контейнер
        self.drag_position = None
    
    def mousePressEvent(self, event:QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            # Используем позицию контейнера, а не самого виджета
            self.drag_position = event.globalPosition().toPoint() - self.container_to_move.pos()
           
        
    def mouseReleaseEvent(self, event:QMouseEvent) -> None:
        self.drag_position = None
        
        
    def mouseMoveEvent(self, event:QMouseEvent) -> None:
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.container_to_move.move(new_pos)  # Перемещаем контейнер
            print(f"Перемещение контейнера в: {new_pos.x()}, {new_pos.y()}")

class ScreenSelector(QMainWindow):
    """Создает выделение"""
    save_buffer_signal = Signal(int, int, int, int)
    draw_signal = Signal()
    click_save_signal = Signal(int, int, int, int)
    clear_signal = Signal()
    paint_signal = Signal(int, int, int, int)
    exit_signal = Signal()
    clear_paint_signal = Signal()
    slider_update_signal = Signal(int)
    def __init__(self) -> None:
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
        self.paint_signal.emit(self.width_paint,self.height_paint,self.x_paint,self.y_paint)


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
               

        self.buffer_button = QCheckBox("Buffer", self.tool_container)
        self.buffer_button.setObjectName("buffer_button")
        self.buffer_button.clicked.connect(self.click_save_buffer)
        
        self.save_button = QCheckBox("Save", self.tool_container) 
        self.save_button.clicked.connect(self.click_save_button)
        self.save_button.setObjectName("save_button")
        
        self.draw_button = QCheckBox("Draw", self.tool_container) 
        self.draw_button.clicked.connect(self.click_draw_button)
        self.draw_button.setObjectName("draw_button")
        
        self._clear_button = QCheckBox("clear", self.tool_container) 
        self._clear_button .clicked.connect(self.click_clear_paint_button)
        self._clear_button .setObjectName("clear")

        self._slider = QSlider(Qt.Vertical)
        self._slider.setRange(0, 100) # Диапазон от 0 до 100
        self._slider.setValue(self.step)     # Начальное значение
        self._slider.valueChanged.connect(self._slider_update)
        # Добавляем в layout
        layout.addWidget(self._move_button)
        layout.addWidget(self.buffer_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.draw_button)
        layout.addWidget(self._clear_button )
        layout.addWidget(self._slider)
        
        layout.addStretch()
        
        self.tool_container.show()

    def load_step(self,value:int):
        self.step = value

    def _exit(self)-> None:
        self._rubber_band.hide()
        self.clear()
        self.close() # Закрыть окно после выбора
        #self.painter_widget.close()
        
        #Закрытие paint
        self.exit_signal.emit()

    def show_popup(self, message:str)-> None:
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Ошибка")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.exec()        
    
    def clear(self)-> None:
        """Очищает выделение и сбрасывает состояние"""
        #удаление кнопко
        button = ['buffer_button','save_button',
                  'draw_button','_clear_button',
                  '_slider','_move_button']
        
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
    #сигналы    
    def click_save_buffer(self)-> None:
        self.save_buffer_signal.emit(self.x1, self.y1, self.x2, self.y2)
        
    def click_draw_button(self)-> None:
        self.draw_signal.emit()

    def click_save_button(self)-> None:
        self.click_save_signal.emit(self.x1, self.y1, self.x2, self.y2)
        self._exit()

    def click_clear_paint_button(self)-> None:
        self.clear_paint_signal.emit()

    def _slider_update(self,value)-> None:
        self.slider_update_signal.emit(value)