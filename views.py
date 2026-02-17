#views.py
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QLineEdit,
                                 QSystemTrayIcon, QMenu,QCheckBox,
                                QMessageBox,QRubberBand,QGridLayout,QVBoxLayout,QSlider)
from PySide6.QtCore import Qt, QRect, QSize, Signal
from PySide6.QtGui import ( QAction ,QRegion,QPainter,QColor,
                           QMouseEvent,QPaintEvent,QPen,
                           QPixmap,QCloseEvent)
from PySide6.QtWidgets import (QWidget,QMainWindow,QApplication,)

from model import config

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
        


class View(QMainWindow):
    """Создает основное окно программы"""
    search_signal = Signal()
    hot_key_button_signal = Signal()
    close_event_signal = Signal(object)
    def __init__(self) -> None:
        super().__init__()
        self.load_ui()
        self.init_tray()
        
    def init_tray(self)-> None:   
        """Создает объект для системного трея""" 
        if not hasattr(self,"tray_icon"):
            self.tray_icon = QSystemTrayIcon(self)    
        self.resize(300, 200)
        # Используйте свою иконку, например: QIcon("icon.png")
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))                 
    
    def load_ui(self)-> None:
        """Настройка пользовательского интерфейса"""
        self.setMinimumHeight(config.app_min_height)
        self.setMinimumWidth(config.app_min_width)
        self.setWindowTitle(config.app_name)  

        #  Создаем центральный виджет 
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)  
        
        #Кнопки и интерфейсы первая строка
        self._label_save = QLabel("Куда сохранить")
        self._input_path = QLineEdit()
        self._search_button = QPushButton("Обзор")
        self._search_button.clicked.connect(self.click_search_signal)
        #Кнопки и интерфейсы Вторая строка
        self._label_hot_key = QLabel("Сделать скрин")
        self._hot_key_button = QPushButton("ctrl+shift")
        self._hot_key_button.clicked.connect(self.click_hot_key_signal)
        self._status_label = QLabel(" ")

        #Первая строка
        layout.addWidget(self._label_save, 0, 0,)
        layout.addWidget(self._input_path, 0, 1)
        layout.addWidget(self._search_button, 0, 2)

        #Вторая строка 
        layout.addWidget(self._label_hot_key, 1, 0)
        layout.addWidget(self._hot_key_button, 1, 1)
        layout.addWidget(self._status_label, 1, 2)


        #ПРижимет кверху
        layout.setRowStretch(0, 0)    
        layout.setRowStretch(1, 0)   
        layout.setRowStretch(2, 1)    
        self.show()
    
    def closeEvent(self,event:QCloseEvent)-> None:
        self.close_event_signal.emit(event)

    def click_hot_key_signal(self)-> None:
        self.hot_key_button_signal.emit()

    def click_search_signal(self)-> None:
        self.search_signal.emit()

    def input_text(self,path:str)-> None:
        self._input_path.setText(path)

    def status_label_prepare(self)-> None:
        self._status_label.setText("Подготовка")

    def status_label_ready(self)-> None:
        self._status_label.setText(" ")

    def update_btn(self,text)-> None:
        self._hot_key_button.setText(text)      

    def load_hot_key(self,text:str)-> None:
        self._hot_key_button.setText(text)

    def return_input_text(self)-> str:
        return self._input_path.text()
        
    def show_tray(self)-> None:
        """Показывает сам трей ,созданный ранее"""
        #self.icon_tray = QIcon("icon/copy.png")

        # Меню трея
        self.tray_menu = QMenu()
        self.show_action = QAction("Показать", self)
        self.quit_action = QAction("Выход", self)
        
        self.show_action.triggered.connect(self.showNormal)
        self.quit_action .triggered.connect(QApplication.instance().quit)
    
        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addAction(self.quit_action )
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        self.tray_icon.showMessage(
        "Приложение свернулось в трей",
        "Для скриншота нажми горячие клавишы",
        QSystemTrayIcon.MessageIcon.Information,
        2000
    )       

    def message_save_buffer(self):
        """Выходит при сохранении в буфер обмена"""
        self.tray_icon.show()
        self.tray_icon.showMessage(
        "Успешно",
        "Сохранено в буфер обмена",
        QSystemTrayIcon.MessageIcon.Information,
        2000
    )       
        
