#views.py
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QLineEdit,
                                QFileDialog, QSystemTrayIcon, QMenu,QCheckBox,QComboBox,
                                QMessageBox,QRubberBand,QColorDialog,QGridLayout,QVBoxLayout)
from log import *
from PySide6.QtCore import Qt, QRect, QSize, QThread, Signal,QSettings ,qDebug, qInfo, qWarning, qCritical
from PySide6.QtGui import QKeySequence, QShortcut,  QAction ,QRegion,QPainter,QImage,QColor,QBrush, QIcon

import win32clipboard
from PySide6.QtWidgets import QWidget

class ScreenSelector(QMainWindow):
    """Создает то самое выделение"""
    save_buffer_signal = Signal(int, int, int, int)
    draw_signal = Signal()
    click_save_signal = Signal(int, int, int, int)
    def __init__(self):
        super().__init__()
        # Окно на весь экран, без рамок, поверх остальных
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.setWindowOpacity(0.6) 
        self.setWindowState(Qt.WindowFullScreen)
        self.setStyleSheet("background-color: rgba(0, 0, 0,255);") 
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = None
        self.screen_on = True
        
    def clear(self):
        """Очищает выделение и сбрасывает состояние"""
        #удаление кнопко
        if hasattr(self, 'buffer_button'):
            self.buffer_button.deleteLater()
        if hasattr(self, 'save_button'):
            self.save_button.deleteLater()
        if hasattr(self, 'draw_button'):
            self.draw_button.deleteLater()  
        # Скрываем резиновую ленту
        self.rubber_band.hide()
        # Сбрасываем переменные состояния
        self.origin = None
        self.selected_rect = None
        self.screen_on = True
        # Убираем маску окна (если была установлена)
        self.clearMask()
        # Сбрасываем геометрию резиновой ленты
        self.rubber_band.setGeometry(QRect())
        # Перерисовываем окно
        self.update()
        # Возвращаем полностью затемненный экран
        self.setStyleSheet("background-color: rgba(0, 0, 0, 255);") 

    def mousePressEvent(self, event):
        if self.screen_on:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()
            self.screen_on = False
        else:
            self.exit()    
    def mouseMoveEvent(self, event):
        if self.origin:
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        self.selected_rect = self.rubber_band.geometry()
        self.x, self.y, self.width, self.height = self.rubber_band.geometry().getRect()
        self.x1, self.y1, self.x2, self.y2 = self.x, self.y, self.x + self.width, self.y + self.height
        self.create_selection_hole()
        self.load_screen_ui()
        
    def create_selection_hole(self):
        """Создает 'дырку' в затемненном экране"""
        if not self.selected_rect:
            return
        #Получаем размер всего экрана
        screen_rect = self.screen().geometry()
        #Устанавливем регион весь экран
        region = QRegion(screen_rect)
        #Вычитаем выделеныые 
        region = region.subtracted((self.selected_rect))
        
        #Устанавливем 
        self.setMask(region)    
        
    def load_screen_ui(self):
        # Получаем координаты справа от выделенной области
        x = self.selected_rect.x() + self.selected_rect.width()
        y = self.selected_rect.y()
        
        # Создаем контейнер для виджетов
        self.tool_container = QWidget(self)
        self.tool_container.setGeometry(x, y, 150, 200)  # x, y, width, height
        
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
        
        # Добавляем в layout
        layout.addWidget(self.buffer_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.draw_button)
        #layout.addStretch()
        
        self.tool_container.show()
        
    def exit(self):
        self.rubber_band.hide()
        self.clear()
        self.close() # Закрыть окно после выбора

    def click_save_button(self):
        self.click_save_signal.emit(self.x1, self.y1, self.x2, self.y2)
        self.exit()

    def show_popup(self, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Ошибка")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.exec()        

    #сигналы    
    def click_save_buffer(self):
        self.save_buffer_signal.emit(self.x1, self.y1, self.x2, self.y2)

    def click_draw_button(self):
        self.draw_signal.emit()


        
class View(QMainWindow):
    search_signal = Signal()
    hot_key_button_signal = Signal()
    close_event_signal = Signal(object)
    def __init__(self):
        super().__init__()
        self.load_ui()
        
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
        self.setWindowTitle("Трей-приложение")
        self.resize(300, 200)

        # --- Настройка трея ---
        self.tray_icon = QSystemTrayIcon(self)
        # Используйте свою иконку, например: QIcon("icon.png")
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)) 
        
        # Меню трея
        tray_menu = QMenu()
        show_action = QAction("Показать", self)
        quit_action = QAction("Выход", self)
        
        show_action.triggered.connect(self.showNormal)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.showMessage(
            "Приложение свернулось в трей",
            "Ждя скриншота нажми горячие клавишы",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )        