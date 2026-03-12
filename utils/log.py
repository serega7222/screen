#utils/log.py
import logging

def colored_message(level, message)-> str :
    """Добавляет цвет к сообщению"""
    colors = {
        'INFO': '\033[94m',     # Синий
        'WARNING': '\033[93m',  # Желтый
        'ERROR': '\033[91m',    # Красный
        'SUCCESS': '\033[92m',  # Зеленый
        'RESET': '\033[0m'
    }
    
    color = colors.get(level, colors['RESET'])
    return f"{color}[{level}] {message}{colors['RESET']}"

class ColoredLogger:
    def __init__(self)-> None :
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def info(self, msg)-> None :
        print(colored_message('INFO', msg))
    
    def warning(self, msg)-> None :
        print(colored_message('WARNING', msg))
    
    def error(self, msg)-> None :
        print(colored_message('ERROR', msg))
    
    def success(self, msg)-> None :
        print(colored_message('SUCCESS', msg))

logger = ColoredLogger()