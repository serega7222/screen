#views.py
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QLineEdit,
                                QFileDialog, QSystemTrayIcon, QMenu,QCheckBox,QComboBox,
                                QMessageBox,QRubberBand,QColorDialog)
from log import *
from PySide6.QtCore import Qt, QRect, QSize, QThread, Signal,QSettings ,qDebug, qInfo, qWarning, qCritical
from PySide6.QtGui import QKeySequence, QShortcut,  QAction ,QRegion,QPainter,QImage,QColor,QBrush
from PIL import  ImageGrab
import io
import win32clipboard

class ScreenSelector(QMainWindow):
    """Создает то самое выделение"""
    save_buffer_signal = Signal(int, int, int, int)
    draw_signal = Signal()
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
        self.buffer_button.deleteLater()
        self.save_button.deleteLater()
        self .draw_button.deleteLater()        
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
        
        x = self.selected_rect.x() + (self.selected_rect.width()) 
        y = self.selected_rect.y() + (self.selected_rect.height() )


        self.buffer_button = QCheckBox(self)
        self.buffer_button.move(x,y-30)
        self.buffer_button.setObjectName("buffer_button")
        self.buffer_button.clicked.connect(self.click_save_buffer)
        self.buffer_button.show()

        self.save_button = QCheckBox(self) 
        self.save_button.move(x,y-60)
        self.save_button.clicked.connect(self.click_save_button)
        self.save_button.setObjectName("save_button")
        self.save_button.show()

        
        self.draw_button = QCheckBox(self) 
        self.draw_button.move(x,y-90)
        self.draw_button.clicked.connect(self.click_draw_button)
        self.draw_button.setObjectName("draw_button")
        self.draw_button.show()


                      
    def exit(self):
        self.rubber_band.hide()
        self.clear()
        self.close() # Закрыть окно после выбора

    def click_save_button(self):
        print("Нажато сохранить на пк")
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
    def __init__(self):
        super().__init__()
        self.load_ui()
        
    def load_ui(self):
        """Настройка пользовательского интерфейса"""
        try:
            logger.info("Попытка загрузить ui интерфейс")
            self.setFixedSize(500, 400)
            self.setWindowTitle("Скриншотер экрана")    
            #Кнопки и интерфейсы
            self.lable_save = QLabel("Куда сохранить",self)
            self.inp = QLineEdit(self)
            self.inp.move(100,2)
            self.inp.resize(300,25)
            self.search_button = QPushButton("Обзор",self)
            self.search_button.move(400,0)
            self.search_button.clicked.connect(self.click_search_signal)
            self.lable_hot_key = QLabel("Сделать скрин",self)
            self.lable_hot_key.move(0,50)
            self.hot_key_button = QPushButton("ctrl+shift",self)
            self.hot_key_button.move(100,50)
            self.hot_key_button.clicked.connect(self.click_hot_key_signal)
            self.status_lable = QLabel(" ",self)
            self.status_lable.move(200,50)
            self.show()
            logger.success("Интерфейс ui успешно загружен")
            
        except Exception as e:
            logger.error(f"Не удалось загрузить интерфейс {e}")

    def click_hot_key_signal(self):
        self.hot_key_button_signal.emit()

    def click_search_signal(self):
        self.search_signal.emit()

    def input_text(self,path):
        self.inp.setText(path)

    def status_lable_prepare(self):
        self.status_lable.setText("Подготовка")

    def status_lable_ready(self):
        self.status_lable.setText(" ")

    def update_btn(self,text):
        self.hot_key_button.setText(text)      

    def load_hot_key(self,text):
        self.hot_key_button.setText(text)

