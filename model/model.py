#model/model.py
from dataclasses import dataclass
from PySide6.QtCore import QSettings 
from utils.log import logger
from typing import Optional

@dataclass
class AppConfig():
    app_name : str = "Скриншотер экрана"
    app_min_height : int = 100
    app_min_width : int  = 500
    default_color : str = "blue"
    default_pen_size : int = 1
    default_hot_key : str = "shift + ctrl"
    
config = AppConfig()




class Model():
    """Отвечает за загрузку и сохранение данных"""
    def __init__(self)-> None: 
        self.settings = QSettings("MyApp", "Screenshotter")
    
    def save_path(self,path:str)-> None:
        """Сохраняет путь  в реестре 
        путь сохранения  HKEY_CURRENT_USER\SOFTWARE\MyApp """
        self.settings.setValue("save_path", path)
        
    def load_path(self) -> Optional[str]:
        """Загружает сохраненный путь."""
        path = self.settings.value('save_path')
        if path :
            return path
        else:
            logger.info("Пути нет")
            return None
        
    def save_hot_key(self,key:str)-> None: 
        """Сохраняет горячие клавиши"""
        try:
            self.settings.setValue('hot_key',key)
            logger.success("Горячие клавиши сохранены")
        except Exception as e :
            logger.error(f"Произошла ошибка при сохранении горячих клавиш {e}")

    def load_hot_key(self)-> Optional[str]:
        "Загружает горячие клавиши"
        try:
            key = self.settings.value('hot_key') 
            if key :
                return key  
            else:
                logger.info("Горячие кнопки не обнаружены")
                return config.default_hot_key
        except Exception as e :
            logger.error(f"Ошибка при загрузке горячих клавиш {e}") 
            return None

    def load_pen_size(self) -> int :
        """Загружает размер ручки для рисования если она есть ,если нет то загружает стандартный размер"""
        pen_size = self.settings.value('pen_size') 
        if pen_size :
            return pen_size
        else:
            return config.default_pen_size

    def save_pen_size(self,size:int) -> None :
        """Сохраняет размер ручки"""
        self.settings.setValue("pen_size", size)

    def save_color(self,color:str)  -> None :
        """Сохраняет цвет ручки"""
        self.settings.setValue("color", color) 
        logger.info(f"Сохранил цвет ручки {color}")

    def save_marker_color(self,color:str)-> None :
        """Сохраняет цвет маркера"""
        self.settings.setValue("marker_color", color) 
        logger.info(f"Сохранил цвет маркера {color}")

    def load_color(self) -> str :
        """Загружает цвет ручки если нет цвета ,то загружает стандартный цвет"""
        color = self.settings.value('color')
        logger.info(f"Загрузил цвет {color}")
        if color :
            return color
        else:
            return config.default_color  
        
    def load_marker_color(self)-> str :     
        """Загружает цвет маркера если нет цвета ,то загружает стандартный цвет"""
        marker_color = self.settings.value('marker_color')
        if marker_color:
            return marker_color
        else:
            return config.default_color  