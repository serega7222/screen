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
from view.tool_panel import ToolPanel

class SaveMode():
    BUFFER = "buffer"
    LOCAL = "local"

class SaveControll():
    """Отвечает за сохранение  в буффере обмена либо локально на пк"""
    def __init__(self,screen:ScreenSelector,tray:Tray,main:MainScreen,tool_panel:ToolPanel)-> None:
        self.tool_panel = tool_panel
        self.screen = screen
        self.tray = tray
        self.main = main
        self._connect_signal()

    def _connect_signal(self)-> None:
        """Принимает сигналы из view/selector_screen.py в зависимости от нажатой кнопки передаются разные режимы сохранения"""

        self.tool_panel.save_buffer_signal.connect(
            lambda x1, y1, x2, y2: self._save(x1, y1, x2, y2, SaveMode.BUFFER)
        )
        self.tool_panel.save_local_signal.connect(
            lambda x1, y1, x2, y2: self._save(x1, y1, x2, y2, SaveMode.LOCAL)
        )

    @Slot(int, int, int, int)     
    def _save(self,x1:int, y1:int, x2:int, y2:int,mode:SaveMode)-> None:
        """Функция срабатывает при получении сигнала  из view/selector_screen.py 
        Args:
            x1, y1: координаты левого верхнего угла выделенной области
            x2, y2: координаты правого нижнего угла выделенной области
            mode: режим сохранения (SaveMode.BUFFER или SaveMode.LOCAL)  
        Note:
            Перед сохранением проверяет, что область выделения не пустая.
            При ошибках показывает всплывающее окно и логирует проблем     
        """
        
        """Проверяет не пустое ли выделение"""
        if x1 >= x2 or y1 >= y2:
            self.screen.exit()
            self.screen.show_popup("Нельзя сделан скриншот пустого пространства")
            logger.info("Попытка сделать скриншот пустого окна")
            return None           
        self.img = ImageGrab.grab(bbox=(x1, y1, x2,y2))

        if mode == "buffer":
            """Сохраняет в буффер"""
            try:
                logger.info("Нажато 'сохранить в буфер'")
                self.output = io.BytesIO()
                self.img.convert('RGB').save(self.output, 'BMP')
                data = self.output.getvalue()[14:]  
                self.output.close()
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard() 
                logger.success("Успешно сохранено в буфер")                  
                self.tray.message_save_buffer()    
            except Exception as e :
                self.screen.show_popup(f"{e}")
                logger.error("Ошибка,не удалось сохранить в буффер")  
            finally:
                self.screen.exit()
        elif mode == "local":
            """Сохраняет локально"""
            try :
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_folder = self.main .get_input_path()
                filename = f"screenshot_{timestamp}.png"
                save_path = os.path.join(save_folder, filename)
                self.img.save(save_path, "PNG")
                logger.success("Сохранено на пк")
                self.tray.message_save_local(save_path)                
            except FileNotFoundError :
                logger.error(f"произошла ошибка некоректный путь сохранения")
                self.screen.show_popup(f"Укажи корректный путь сохранения")
            except Exception as e :
                logger.error(f"произошла ошибка {e}")
                self.screen.show_popup(f"Ошибка {e}")            

            finally:
                self.screen.exit()