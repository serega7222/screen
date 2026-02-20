#controllers/main_screen_controller.py
from PySide6.QtCore import Qt,  QThread, Signal,Slot
from PySide6.QtWidgets import QFileDialog ,QColorDialog    
from log import logger
from model import Model
from view.main_screen import MainScreen
from controllers.hot_key  import HotKey 

class MainScreenController():
    """Отвечает за главное окно ,которое появляется первым"""
    def __init__(self,screen:MainScreen,th:HotKey,model:Model):
        self.main_screen = screen
        self.th = th 
        self.model = model
        self.connect_signal()
    def connect_signal(self)-> None:
        self.main_screen.search_signal.connect(self.push_search_button)
        self.main_screen.hot_key_button_signal.connect(self.click_hot_button)
        self.main_screen.close_event_signal.connect(self.close_event)          

    #кнопка обзор  
    @Slot()  
    def push_search_button(self)-> None:
        logger.info("Нажата кнопка путь сохранения")
        try:
            logger.info("Открыто окно выбора папки")
            self.folder = QFileDialog.getExistingDirectory(
                self.main_screen,  # родительское окно
                "Выберите папку",  # заголовок
                "",  # начальная директория
                QFileDialog.Option.ShowDirsOnly  # опции
            )  
            if self.folder:
                self.model.save_path(self.folder)
                self.main_screen.input_text(self.folder)
                logger.success("Папка выбрана путь сохранен в HKEY_CURRENT_USER\SOFTWARE\MyApp")

            else:
                logger.info("Папка отменина")
        except Exception as e:
            logger.error(f"Проблемма с кнопкой обзор {e}")  

    def click_hot_button(self)-> None:
        self.th.start()
        self.main_screen.status_label_prepare()            

    @Slot()
    def close_event(self)-> None:
        self.main_screen.show_tray()