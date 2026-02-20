#controllers/hot_key.py
from PySide6.QtCore import  QThread, Signal 
import keyboard
from log import logger
from keyboard import KeyboardEvent

class HotKey(QThread):
    """Отслеживает горячие клавишы"""
    hot_key_signal = Signal(str)
    screen_signal = Signal()
    def __init__(self)-> None:
        super().__init__()
        self.lst_hot_key = set()
        
    def run(self)-> None:
        self.flag = True
        keyboard.on_press(self.key_pressed)
        logger.info("Отслеживание нажатий")
        while self.flag:
            self.msleep(100)  # Не грузит CPU

    def check_press_hot_key(self)-> None:
        keyboard.add_hotkey('ctrl+shift', self.trigger_hotkey)

    def trigger_hotkey(self)-> None: 
        logger.info("Нажаты горячие клавишы")
        self.screen_signal.emit()

    def key_pressed(self,event:KeyboardEvent)-> None:
        
        if self.flag:
            self.lst_hot_key.add(event.name)
            if len(self.lst_hot_key) == 2 :
                text = "+".join(self.lst_hot_key)
                self.hot_key_signal.emit(text)
                self.lst_hot_key.clear()
                self.pause()
            
    def pause(self)-> None:
        self.flag = False

    def stop(self)-> None:
        keyboard.unhook_all()
        super().quit() 