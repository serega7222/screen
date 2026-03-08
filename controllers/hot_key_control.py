#controllers/hot_key_control.py
from PySide6.QtCore import  QThread, Signal 
import keyboard
from keyboard import KeyboardEvent
from utils.log import logger


class WatchPress(QThread):
    """Отслеживает горячие клавишы """
    change_hot_key_signal = Signal(str)
    key_pressed_signal = Signal()

    def __init__(self)-> None:
        super().__init__()
        self.lst_hot_key = set()
        
    def run(self)-> None:
        """Срабатывает при нажатие кнопки горячие клавишы"""
        self.flag = True
        keyboard.on_press(self.key_pressed)
        logger.info("Отслеживание нажатий")
        while self.flag:
            self.msleep(100)  



    def trigger_hotkey(self)-> None: 
        """Срабатывает если нажаты клавиши из функции check_press_hot_key 
        посылает сигнал в main_screen_controll.py 
        
        
        """
        logger.info("Нажаты горячие клавишы")
        self.key_pressed_signal.emit()

    def key_pressed(self,event:KeyboardEvent)-> None:

        if self.flag:
            self.lst_hot_key.add(event.name)
            if len(self.lst_hot_key) == 2 :
                text = "+".join(self.lst_hot_key)
                self.change_hot_key_signal.emit(text)
                self.lst_hot_key.clear()
                self.pause()
            
    def pause(self)-> None:
        self.flag = False

    def stop(self)-> None:
        keyboard.unhook_all()
        super().quit() 

    def check_press_hot_key(self)-> None:
        """Включается в main.py нужна что бы отслеживать нажаты ли горячие клавиши """
        keyboard.add_hotkey('ctrl+shift', self.trigger_hotkey)        