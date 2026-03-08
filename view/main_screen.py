#view/main_screen.py
from PySide6.QtCore import  Signal
from PySide6.QtWidgets import (QMainWindow, QPushButton, QLabel, 
                                QLineEdit, QGridLayout, QWidget)

                           
from model.model import config

class MainScreen(QMainWindow):
    """Создает основное окно программы оно появляется при старте программы"""
    signal_search_btn = Signal()
    signal_hot_key = Signal()
    
    def __init__(self) -> None:
        super().__init__()
        self.load_ui()


    def load_ui(self)-> None:
        """Загрузка интерфейса главного окна"""
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
        _layout.addWidget(self._label_save, 0, 0)
        _layout.addWidget(self._path, 0, 1)
        _layout.addWidget(self._search_button, 0, 2)

        #Вторая строка 
        _layout.addWidget(self._label_hot_key, 1, 0)
        _layout.addWidget(self._hot_key_button, 1, 1)
        _layout.addWidget(self._status_label, 1, 2)


        #Прижимает кверху
        _layout.setRowStretch(0, 0)    
        _layout.setRowStretch(1, 0)   
        _layout.setRowStretch(2, 1)    
        self.show()


 
    #сигналы
    def _click_search(self)-> None:
        """Сигнал посылается в main_screen_control.py срабатывает при нажатии кнопки обзор"""
        self.signal_search_btn.emit()           

    def _hot_key_(self)-> None:
        """Сигнал посылается в main_screen_control.py при нажатии кнопки горячие клавиши"""
        self.signal_hot_key.emit()   
        
    #Публичные методы
    def change_input_text(self,text)-> None:
        """Вызывается из main_screen_control.py из функции _open_dialog и   _load_main_setting  меняет текст в QlineEdit"""
        self._path.setText(text)

    def change_btn_text(self,text)-> None:
        """Вызывается из controllers/main_screen_control.py, функция _change_hot_key, меняет текст в кнопке"""
        self._hot_key_button.setText(text)

    def get_input_path(self)-> str:
        """Возвращает то, что введено в QLineEdit вызывается в controllers\save_controll.py в функции _save"""
        return  self._path.text()  

       