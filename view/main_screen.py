#view/main_screen.py
from PySide6.QtCore import  Signal
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QLineEdit,
                                 QSystemTrayIcon, QMenu,QGridLayout)
from PySide6.QtWidgets import (QWidget,QMainWindow,QApplication,)
from PySide6.QtGui import ( QAction ,QCloseEvent)
                           
from model import config

class MainScreen(QMainWindow):
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
        