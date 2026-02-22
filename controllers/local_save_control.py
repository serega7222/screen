#controllers/local_save_control.py
from view.screen_selector import ScreenSelector
from view.main_screen import MainScreen
from view.tray import Trey
from utils.log import logger
from PIL import  ImageGrab
from PySide6.QtCore import  Slot
from datetime import datetime
import os

class LocalSave():
    def __init__(self,screen:ScreenSelector,trey:Trey,main:MainScreen)-> None:
        "Сохранение локально на пк"
        self.screen = screen
        self.trey = trey
        self.main = main
        self.screen.save_local_signal.connect(self.save_local)

    @Slot(int, int, int, int) 
    def save_local(self,x1, y1, x2, y2)-> None:
        try:
            if x1 >= x2 or y1 >= y2:
                self.screen._exit()
                self.screen.show_popup("Нельзя сделан скриншот пустого пространства")
                logger.info("Попытка сделать скриншот пустого окна")
                return None            
            screenshot = ImageGrab.grab(bbox=(x1, y1,x2, y2))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_folder = self.main .get_input_path()
            filename = f"screenshot_{timestamp}.png"
            save_path = os.path.join(save_folder, filename)
            screenshot.save(save_path, "PNG")
            self.screen._exit()
            logger.success("Сохранено на пк")
            self.trey.message_save_local(save_path)
        except FileNotFoundError :
            self.screen._exit()
            logger.error(f"произошла ошибка некоректный путь сохранения")
            self.screen.show_popup(f"Укажи корректный путь сохранения")
        except Exception as e :
            self.screen._exit()
            logger.error(f"произошла ошибка {e}")
            self.screen.show_popup(f"Ошибка {e}")