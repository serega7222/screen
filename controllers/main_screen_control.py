#controllers/main_screen_control.py
from PySide6.QtCore import  Slot
from PySide6.QtWidgets import QFileDialog 
from utils.log import logger
from view.main_screen import MainScreen
from view.screen_selector import ScreenSelector
from model.model import Model
from controllers.hot_key_control import WatchPress



class MainScreenControl():
    """Отвечает за кнопки главного окна"""
    def __init__(self,main_screen:MainScreen,model:Model,watcher:WatchPress,screen:ScreenSelector) -> None:
        self.main_screen = main_screen
        self.model = model
        self.warcher = watcher
        self.screen_selector = screen
        self._load_main_setting()
        self._connect_signal()

    def _connect_signal(self)-> None:
        self.main_screen.signal_search_btn.connect(self._open_dialog)
        self.main_screen.signal_hot_key.connect(self._press_hot_key_btn)
        self.warcher.change_hot_key_signal.connect(self._change_hot_key)
        self.warcher.key_pressed_signal.connect(self._show_selector)
    @Slot()
    def _open_dialog(self)-> None:
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
                self.main_screen.change_input_text(self.folder)
                logger.success("Папка выбрана путь сохранен в HKEY_CURRENT_USER\SOFTWARE\MyApp")

            else:
                logger.info("Папка отменина")
        except Exception as e:
            logger.error(f"Проблемма с кнопкой обзор {e}")  


    def _load_main_setting(self)-> None:
        path = self.model.load_path()
        self.main_screen.change_input_text(path)
    
    @Slot()
    def _press_hot_key_btn(self)-> None:
        self.warcher.start()

    @Slot(str)
    def _change_hot_key(self,text)-> None:
        self.main_screen.change_btn_text(text)

    @Slot()
    def _show_selector(self):
        self.screen_selector.show()