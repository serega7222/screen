from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QLineEdit,
                                QFileDialog, QSystemTrayIcon, QMenu,QCheckBox,QComboBox,
                                QMessageBox,QRubberBand,QColorDialog)

from PySide6.QtCore import Qt, QRect, QSize, QThread, Signal,QSettings ,qDebug, qInfo, qWarning, qCritical
from PySide6.QtGui import QKeySequence, QShortcut,  QAction ,QRegion,QPainter,QImage,QColor,QBrush
import keyboard
from PIL import  ImageGrab
import io
import win32clipboard
import sys
import logging

def colored_message(level, message):
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
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def info(self, msg):
        print(colored_message('INFO', msg))
    
    def warning(self, msg):
        print(colored_message('WARNING', msg))
    
    def error(self, msg):
        print(colored_message('ERROR', msg))
    
    def success(self, msg):
        print(colored_message('SUCCESS', msg))

logger = ColoredLogger()

class ShowHotKey(QThread):
    """Отслеживает горячие клавишы"""
    key_signal = Signal(str)
    lable_status_signal = Signal(str)
    def __init__(self,):
        super().__init__()
        self.lst = set()
        

    def run(self):
        keyboard.on_press(self.key_pressed)
        self.flag = True
        while self.flag:
            self.msleep(100)

    def key_pressed(self,event):
        if self.flag:
            self.lst.add(event.name)
            if len(self.lst) == 2 :
                new = " ".join(self.lst )
                self.key_signal.emit(new )
                self.lst.clear()
                self.flag = False
                logger.info("Установлены горячие клавишы")
                self.lable_status_signal.emit("Готово")  
    def quit(self):
        keyboard.unhook_all()
        super().quit() 
        
class HotkeyThread(QThread):
    hotkey_triggered = Signal()
    logger.info("Горячие клавиши отслеживаются")
    def __init__(self):
        super().__init__()
        self.running = True
    def run(self):
        # Регистрируем глобальную горячую клавишу Ctrl+S
        keyboard.add_hotkey('ctrl+shift', self.trigger_hotkey)
        # Блокируем поток, пока не будет остановлен
        keyboard.wait()
    def trigger_hotkey(self):
        self.hotkey_triggered.emit()
    def stop(self):
        self.running = False
        keyboard.unhook_all()

class Model():
    def __init__(self):
        self.settings = QSettings("MyApp", "Screenshotter")


class ScreenSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        # Окно на весь экран, без рамок, поверх остальных
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.setWindowOpacity(0.6) 
        self.setWindowState(Qt.WindowFullScreen)
        self.setStyleSheet("background-color: rgba(0, 0, 0,255);") 
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = None
        self.screen_on = True
        
    def mousePressEvent(self, event):
        if self.screen_on:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()
            self.screen_on = False
        else:
            self.exit()    
    def mouseMoveEvent(self, event):
        if self.origin:
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        self.selected_rect = self.rubber_band.geometry()
        self.x, self.y, self.width, self.height = self.rubber_band.geometry().getRect()
        self.x1, self.y1, self.x2, self.y2 = self.x, self.y, self.x + self.width, self.y + self.height
        self.create_selection_hole()
        self.load_screen_ui()
        
    def create_selection_hole(self):
        """Создает 'дырку' в затемненном экране"""
        if not self.selected_rect:
            return
        #Получаем размер всего экрана
        screen_rect = self.screen().geometry()
        #Устанавливем регион весь экран
        region = QRegion(screen_rect)
        #Вычитаем выделеныые 
        region = region.subtracted((self.selected_rect))
        #Устанавливем 
        self.setMask(region)    
        
    def load_screen_ui(self):
        
        x = self.selected_rect.x() + (self.selected_rect.width()) 
        y = self.selected_rect.y() + (self.selected_rect.height() )


        self.buffer_button = QCheckBox(self)
        self.buffer_button.move(x,y-30)
        self.buffer_button.setObjectName("buffer_button")
        self.buffer_button.clicked.connect(self.click_save_buffer)
        self.buffer_button.show()

        self.save_button = QCheckBox(self) 
        self.save_button.move(x,y-60)
        self.save_button.clicked.connect(self.click_save_button)
        self.save_button.setObjectName("save_button")
        self.save_button.show()

        
        self.draw_button = QCheckBox(self) 
        self.draw_button.move(x,y-90)
        self.draw_button.clicked.connect(self.click_draw_button)
        self.draw_button.setObjectName("draw_button")
        self.draw_button.show()

    def click_draw_button(self):
        dialog = QColorDialog()
        dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        dialog.setStyleSheet("""
            QColorDialog, QWidget {
                background-color: white;
                color: black;
            }
        """)
        
        dialog.setCurrentColor(QColor(Qt.black))
        
        if dialog.exec():
            color = dialog.selectedColor()
            if color.isValid():
                print(f"Выбран цвет: {color.name()}") 
                
                           
    def exit(self):
        self.rubber_band.hide()
        self.close() # Закрыть окно после выбора

    def click_save_button(self):
        print("Нажато сохранить на пк")
        self.exit()

    def show_popup(self, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Ошибка")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.exec()        
        
    def click_save_buffer(self):
        try:
            logger.info("Нажато сохрнаить в буфере")
            self.img = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2))
            self.output = io.BytesIO()
            self.img.convert('RGB').save(self.output, 'BMP')   
            data = self.output.getvalue()[14:]  # Убираем заголовок BMP
            self.output.close()
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard() 
            logger.success("Успешно сохраненно в буфер")                  
            self.exit()  
            #playsound('sound\sound.mp3')
            
        except Exception as e :
            if str(e) == "tile cannot extend outside image":
                self.exit()
                self.show_popup("Нельзя сделан скриншот пустого пространства")
                logger.info("Попытка сделать скриншот пустого окна")
            else:
                self.exit()
                self.show_popup(f"{e}")
                logger.error("Ошибка,не удалось сохранить в буффер")

class View(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui()
    def load_ui(self):
        """Настройка пользовательского интерфейса"""
        try:
            logger.info("Попытка загрузить ui интерфейс")
            self.setFixedSize(500, 400)
            self.setWindowTitle("Скриншотер экрана")    
            #Кнопки и интерфейсы
            self.lable_save = QLabel("Куда сохранить",self)
            self.inp = QLineEdit(self)
            self.inp.move(100,2)
            self.inp.resize(300,25)
            self.search_button = QPushButton("Обзор",self)
            self.search_button.move(400,0)
            self.lable_hot_key = QLabel("Сделать скрин",self)
            self.lable_hot_key.move(0,50)
            self.hot_key_button = QPushButton("ctrl+shift",self)
            self.hot_key_button.move(100,50)


            self.status_lable = QLabel("",self)
            self.status_lable.move(200,50)
            self.show()
            logger.success("Интерфейс ui успешно загружен")
            
        except Exception as e:
            logger.error(f"Не удалось загрузить интерфейс {e}")
    def set_path(self,path):
        self.inp.setText(path)
        logger.success("Успешно вставился путь")

    def change_hot_key(self,text):
        self.hot_key_button.setText(text)
    
    def update_status_label(self, text):
        """Обновляет текст статусной метки"""
        self.status_lable.setText(text)
        logger.info(f"Статус обновлен: {text}")    
    
class  Controller():
    def __init__(self):
        """Создаёт и запускает приложение скриншотера."""
        self.view = View()
        self.model = Model()
        self.th = ShowHotKey()
        
        self.hotkey_thread = HotkeyThread()
        self.connect_signals()
        self.load_setting()
        self.hotkey_thread.hotkey_triggered.connect(self.run_screen)
        self.hotkey_thread.start()        
    def run_screen(self):
        self.screen = ScreenSelector()
        self.screen.show()
    def connect_signals(self):
        self.view.search_button.clicked.connect(self.push_search_button)
        self.view.hot_key_button.clicked.connect(self.set_hot_key)
        self.view.destroyed.connect(self.stop_hot_key)

    def stop_hot_key(self):
        self.th.quit()
        logger.info("Закрыли программу")    

    def push_search_button(self):
        logger.info("Нажата кнопка путь сохранения")
        try:
            logger.info("Открыто окно выбора папки")
            self.folder = QFileDialog.getExistingDirectory(
                self.view,  # родительское окно
                "Выберите папку",  # заголовок
                "",  # начальная директория
                QFileDialog.Option.ShowDirsOnly  # опции
            )  
            if self.folder:
                self.model.settings.setValue("save_path",self.folder)
                logger.success("Папка выбрана путь сохранен в HKEY_CURRENT_USER\SOFTWARE\MyApp")

            else:
                logger.info("Папка отменина")
        except Exception as e:
            logger.error(f"Проблемма с кнопкой обзор {e}") 

    def set_hot_key(self):
        logger.info("Нажато установить горячую клавишу")
        self.view.update_status_label("Установка...")
        self.th.key_signal.connect(self.view.change_hot_key)
        self.th.lable_status_signal.connect(self.view.update_status_label)
        self.th.start()

        
    def load_setting(self):
        try:
            logger.info("Попытка загрузить настройки")
            path = self.model.settings.value("save_path", )
            if path:
                self.view.set_path(path)
            if not path:
                logger.warning("Нет пути сохранения")
        except Exception as e :
            logger.error("Не удалось загрузить настройки")
    
        
if __name__ == "__main__":
    app = QApplication(sys.argv)  
    style_file = "style.css"  # Замените на путь к вашему файлу стилей
    with open(style_file, "r",encoding="UTF-8") as file:
        app.setStyleSheet(file.read())       
    sh = Controller()
    app.exec()