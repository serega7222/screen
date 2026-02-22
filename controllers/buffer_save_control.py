#controllers/buffer_save_control.py
from view.screen_selector import ScreenSelector
from PySide6.QtCore import  Slot
import win32clipboard
from utils.log import logger
from view.tray import Trey
from PIL import  ImageGrab
import io

class BufferSave():
    """Сохранеяте в буфер обмена"""
    def __init__(self,screen:ScreenSelector,trey:Trey)-> None:
        self.screen = screen
        self.trey = trey
        self.screen.save_buffer_signal.connect(self.save_buffer)  

    @Slot(int, int, int, int) 
    def save_buffer(self,x1, y1, x2, y2)-> None:
        try:
            if x1 >= x2 or y1 >= y2:
                self.screen._exit()
                self.screen.show_popup("Нельзя сделан скриншот пустого пространства")
                logger.info("Попытка сделать скриншот пустого окна")
                return None
            logger.info("Нажато сохрнаить в буфере")
            self.img = ImageGrab.grab(bbox=(x1, y1, x2,y2))
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
            #playsound('sound\sound.mp3')
            self.trey.message_save_buffer()
        except Exception as e :
            self.screen._exit()
            self.screen.show_popup(f"{e}")
            logger.error("Ошибка,не удалось сохранить в буффер")  