#view/main_screen.py
from PySide6.QtCore import  Signal
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QLineEdit,
                                 QSystemTrayIcon, QMenu,QGridLayout)
from PySide6.QtWidgets import (QWidget,QMainWindow,QApplication,)
from PySide6.QtGui import ( QAction ,QCloseEvent)
                           
from model.model import config

class MainScreen(QMainWindow):
    """Создает основное окно программы"""
    signal_search_btn = Signal()
    signal_hot_key = Signal()
    
    def __init__(self) -> None:
        super().__init__()
        self.load_ui()


    def load_ui(self)-> None:
        """Настройка пользовательского интерфейса"""
        self.setMinimumHeight(config.app_min_height)
        self.setMinimumWidth(config.app_min_width)
        self.setWindowTitle(config.app_name)  

        #  Создаем центральный виджет 
        _central_widget = QWidget()
        self.setCentralWidget(_central_widget)
        _layout = QGridLayout(_central_widget)  
        
        #Кнопки и интерфейсы первая строка
        self._label_save = QLabel("Куда сохранить")
        self._path = QLineEdit()

        self._search_button = QPushButton("Обзор")
        self._search_button.clicked.connect(self._click_search)

        #Кнопки и интерфейсы Вторая строка
        self._label_hot_key = QLabel("Сделать скрин")
        self._hot_key_button = QPushButton("ctrl+shift")
        self._hot_key_button.clicked.connect(self._hot_key_)
        self._status_label = QLabel(" ")

        #Первая строка
        _layout .addWidget(self._label_save, 0, 0,)
        _layout .addWidget(self._path, 0, 1)
        _layout .addWidget(self._search_button, 0, 2)

        #Вторая строка 
        _layout .addWidget(self._label_hot_key, 1, 0)
        _layout .addWidget(self._hot_key_button, 1, 1)
        _layout .addWidget(self._status_label, 1, 2)


        #ПРижимет кверху
        _layout .setRowStretch(0, 0)    
        _layout .setRowStretch(1, 0)   
        _layout .setRowStretch(2, 1)    
        self.show()


 
    #сигналы
    def _click_search(self)-> None:
        self.signal_search_btn.emit()           

    def _hot_key_(self)-> None:
        self.signal_hot_key.emit()   
        
    #Публичные методы
    def change_input_text(self,text)-> None:
        self._path.setText(text)

    def change_btn_text(self,text)-> None:
        self._hot_key_button.setText(text)

    def get_input_path(self)-> str:
        return  self._path.text()  

       