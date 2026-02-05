#model.py
from PySide6.QtCore import QSettings 
from log import *

class Model:
    def __init__(self):
        self.settings = QSettings("MyApp", "Screenshotter")
    
    def save_path(self,path):
        self.settings.setValue("save_path", path)
        
    def load_path(self):
        path =  self.settings.value('save_path')
        if path :
            return path
        else:
            logger.info("Пути нет")

    def save_hot_key(self,key):
        try:
            self.settings.setValue('hot_key',key)
            logger.success("Горячие клавишы сохранены")
        except Exception as e :
            logger.error(f"Произошла ошибка при сохранении горячих клавиш {e}")

    def load_hot_key(self):
        try:
            key = self.settings.value('hot_key') 
            if key :
                return key  
            else:
                logger.info("Путь не обноружен")
        except Exception as e :
            logger.error(f"Ошибка при загрузки горячих клваишь {e}")