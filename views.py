#views.py
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QLineEdit,
                                QFileDialog, QSystemTrayIcon, QMenu,QCheckBox,QComboBox,
                                QMessageBox,QRubberBand,QColorDialog,QGridLayout,QVBoxLayout,QSlider)
from log import *
from PySide6.QtCore import Qt, QRect, QSize, QThread, Signal,QSettings ,qDebug, qInfo, qWarning, qCritical
from PySide6.QtGui import QKeySequence, QShortcut,  QAction ,QRegion,QPainter,QImage,QColor,QBrush, QIcon
from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
    QApplication,
    QFileDialog,
    QStyle,
    QColorDialog,
)
from PySide6.QtCore import Qt, Slot, QStandardPaths
from PySide6.QtGui import (
    QMouseEvent,
    QPaintEvent,
    QPen,
    QAction,
    QPainter,
    QColor,
    QPixmap,
    QIcon,
    QKeySequence,
)
import sys
import win32clipboard
from PySide6.QtWidgets import QWidget



class PainterWidget(QWidget):

    def __init__(self,):
        super().__init__()


    def _create(self,width,height,pos_x,pos_y):
        self.setFixedSize(width, height)
        self.move(pos_x,pos_y)
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(QColor(0, 0, 0, 1))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)      
        self.previous_pos = None
        self.painter = QPainter()
        self.pen = QPen()
        self.pen.setColor(QColor("#aa0000"))
        self.pen.setWidth(10)
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        self.show()

    def change_color(self,color):
        self.pen.setColor(QColor(color))

    def clear_paint(self):
        self.pixmap.fill(QColor(0, 0, 0, 1))
        self.update()

    def set_size(self,size):
        self.pen.setWidth(size)

    def paintEvent(self, event: QPaintEvent):
        """Override method from QWidget

        Paint the Pixmap into the widget

        """
        with QPainter(self) as painter:
            painter.drawPixmap(0, 0, self.pixmap)

    def mousePressEvent(self, event: QMouseEvent):
        """Override from QWidget

        Called when user clicks on the mouse

        """
        self.previous_pos = event.position().toPoint()
        QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event: QMouseEvent):
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

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Override method from QWidget

        Called when user releases the mouse

        """
        self.previous_pos = None
        QWidget.mouseReleaseEvent(self, event)

    def start_paint(self,width,height,pos_x,pos_y):
        self._create(width,height,pos_x,pos_y)

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
    def __init__(self):
        super().__init__()
        # Окно на весь экран, без рамок, поверх остальных
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.setWindowOpacity(0.6) 
        self.setWindowState(Qt.WindowFullScreen)
        self.setStyleSheet("background-color: rgba(0, 0, 0,255);") 
        self._rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self._origin = None
        self._screen_on = True

    def mousePressEvent(self, event):
        if self._screen_on:
            self._origin = event.pos()
            self._rubber_band.setGeometry(QRect(self._origin, QSize()))
            self._rubber_band.show()
            self._screen_on = False
        else:
            self._exit()   
             
    def mouseMoveEvent(self, event):
        if self._origin:
            self._rubber_band.setGeometry(QRect(self._origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        self.selected_rect = self._rubber_band.geometry()
        self.x, self.y, self.width, self.height = self._rubber_band.geometry().getRect()
        self.x1, self.y1, self.x2, self.y2 = self.x, self.y, self.x + self.width, self.y + self.height
        self._create_selection_hole()
        self._load_screen_ui()
        
    def _create_selection_hole(self):
        """Создает 'дырку' в затемненном экране"""
        if not self.selected_rect:
            return
        screen_rect = self.screen().geometry()
        region = QRegion(screen_rect)
        region = region.subtracted((self.selected_rect))
        self.setMask(region) 
        self._create_paint()

    def _create_paint(self):
        self.width_paint = self.selected_rect.width()
        self.height_paint =  self.selected_rect.height()
        
        self.x_paint= self.selected_rect.x()
        self.y_paint = self.selected_rect.y()        
        self.paint_signal.emit(self.width_paint,self.height_paint,self.x_paint,self.y_paint)


    def _load_screen_ui(self):
        # Получаем координаты справа от выделенной области
        x = self.selected_rect.x() + self.selected_rect.width()
        y = self.selected_rect.y()
        
        # Создаем контейнер для виджетов
        self.tool_container = QWidget(self)
        self.tool_container.setGeometry(x, y, 150, 300)  # x, y, width, height
        
        # Создаем layout для контейнера
        layout = QVBoxLayout(self.tool_container)
        
        # Создаем кнопки с родителем tool_container
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
        self._slider.setValue(10)     # Начальное значение
        self._slider.valueChanged.connect(self._slider_update)
        # Добавляем в layout
        layout.addWidget(self.buffer_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.draw_button)
        layout.addWidget(self._clear_button )
        layout.addWidget(self._slider)
        layout.addStretch()
        
        self.tool_container.show()
        
    def _exit(self):
        self._rubber_band.hide()
        self.clear()
        self.close() # Закрыть окно после выбора
        #self.painter_widget.close()
        
        #Закрытие paint
        self.exit_signal.emit()
    def show_popup(self, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Ошибка")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.exec()        
    
    def clear(self):
        """Очищает выделение и сбрасывает состояние"""
        #удаление кнопко
        if hasattr(self, 'buffer_button'):
            self.buffer_button.deleteLater()
        if hasattr(self, 'save_button'):
            self.save_button.deleteLater()
        if hasattr(self, 'draw_button'):
            self.draw_button.deleteLater()  
        if hasattr(self, '_clear_button'):
            self._clear_button .deleteLater()  
        if hasattr(self, '_slider'):
            self._slider .deleteLater()              
                      
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
    def click_save_buffer(self):
        self.save_buffer_signal.emit(self.x1, self.y1, self.x2, self.y2)
        
    def click_draw_button(self):
        self.draw_signal.emit()

    def click_save_button(self):
        self.click_save_signal.emit(self.x1, self.y1, self.x2, self.y2)
        self._exit()

    def click_clear_paint_button(self):
        self.clear_paint_signal.emit()

    def _slider_update(self,value):
        self.slider_update_signal.emit(value)


class View(QMainWindow):
    search_signal = Signal()
    hot_key_button_signal = Signal()
    close_event_signal = Signal(object)
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.init_tray()
        
    def init_tray(self):    
        if not hasattr(self,"tray_icon"):
            self.tray_icon = QSystemTrayIcon(self)    
        self.setWindowTitle("Трей-приложение")
        self.resize(300, 200)
        # Используйте свою иконку, например: QIcon("icon.png")
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))                 
    
    def load_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setMinimumHeight(100)
        self.setMinimumWidth(500)
        self.setWindowTitle("Скриншотер экрана")  

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
    
    def closeEvent(self,event):
        
        self.close_event_signal.emit(event)

    def click_hot_key_signal(self):
        self.hot_key_button_signal.emit()

    def click_search_signal(self):
        self.search_signal.emit()

    def input_text(self,path):
        self._input_path.setText(path)

    def status_label_prepare(self):
        self._status_label.setText("Подготовка")

    def status_label_ready(self):
        self._status_label.setText(" ")

    def update_btn(self,text):
        self._hot_key_button.setText(text)      

    def load_hot_key(self,text):
        self._hot_key_button.setText(text)

    def return_input_text(self):
        return self._input_path.text()
        
    def show_tray(self):
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
        self.tray_icon.show()
        self.tray_icon.showMessage(
        "Успешно",
        "Сохранено в буфер обмена",
        QSystemTrayIcon.MessageIcon.Information,
        2000
    )       
        
