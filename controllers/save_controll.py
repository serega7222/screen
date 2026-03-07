#controllers\save_controll.py
from view.screen_selector import ScreenSelector
from view.main_screen import MainScreen
from view.tray import Tray
from PySide6.QtCore import  Slot
import win32clipboard
from utils.log import logger
from PIL import  ImageGrab
import io
import os
from datetime import datetime


class SaveMode():
    BUFFER = "buffer"
    LOCAL = "local"

class SaveControll():
    """Отвечает за сохранение  в буффере обмена либо локально на пк"""
    def __init__(self,screen:ScreenSelector,trey:Tray,main:MainScreen)-> None:
        self.screen = screen
        self.trey = trey
        self.main = main
        self.screen.save_buffer_signal.connect(
            lambda x1, y1, x2, y2: self._save(x1, y1, x2, y2, SaveMode.BUFFER)
        )
        self.screen.save_local_signal.connect(
            lambda x1, y1, x2, y2: self._save(x1, y1, x2, y2, SaveMode.LOCAL)
        )

    @Slot(int, int, int, int)     
    def _save(self,x1:int, y1:int, x2:int, y2:int,mode:SaveMode)-> None:
        """Проверяет не пустое ли выделение"""
        if x1 >= x2 or y1 >= y2:
            self.screen._exit()
            self.screen.show_popup("Нельзя сделан скриншот пустого пространства")
            logger.info("Попытка сделать скриншот пустого окна")
            return None           
        self.img = ImageGrab.grab(bbox=(x1, y1, x2,y2))

        if mode == "buffer":
            """Сохраняет в буффер"""
            try:
                logger.info("Нажато сохрнаить в буфере")
                self.output = io.BytesIO()
                self.img.convert('RGB').save(self.output, 'BMP')
                data = self.output.getvalue()[14:]  
                self.output.close()
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard() 
                logger.success("Успешно сохраненно в буфер")                  
                self.screen._exit()
                self.trey.message_save_buffer()    
            except Exception as e :
                self.screen._exit()
                self.screen.show_popup(f"{e}")
                logger.error("Ошибка,не удалось сохранить в буффер")  
        elif mode == "local":
            """Сохраняет локально"""
            try :
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_folder = self.main .get_input_path()
                filename = f"screenshot_{timestamp}.png"
                save_path = os.path.join(save_folder, filename)
                self.img.save(save_path, "PNG")
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

