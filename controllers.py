#controllers.py
from log import logger
from PySide6.QtWidgets import QFileDialog ,QColorDialog                        
from model import *
from views import *
from PySide6.QtCore import  QThread, Signal
import keyboard
from keyboard import KeyboardEvent
from PIL import  ImageGrab
import io
from datetime import datetime
import os
from PySide6.QtCore import Qt,  QThread, Signal,Slot
import win32clipboard

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


class Controller:
    def __init__(self)-> None:
        self.model = Model()
        self.view = View()
        self.th = HotKey()
        self.screen = ScreenSelector()
        self.paint = PainterWidget()
        self.th.check_press_hot_key()
        self.load_input()
        self.load_hot_key()
        #подключить сигналы
        self.connect_signal()

    #подключает сигналы          
    def connect_signal(self)-> None:
        self.view.search_signal.connect(self.push_search_button)
        self.view.hot_key_button_signal.connect(self.click_hot_button)
        self.view.close_event_signal.connect(self.close_event)
        self.th.hot_key_signal.connect(self.update_btn_text)
        self.th.screen_signal.connect(self.run_screen)
        self.screen.save_buffer_signal.connect(self.click_save_buffer)
        self.screen.draw_signal.connect(self.click_choose_color_button)
        self.screen.click_save_signal.connect(self.click_save_button)
        self.screen.paint_signal.connect(self.create_paint)
        self.screen.exit_signal.connect(self.exit_paint)
        self.screen.clear_paint_signal.connect(self.clear_paint)
        self.screen.slider_update_signal.connect(self.set_brush_size)
        self.paint.size_pen_signal.connect(self.load_paint_setting)
    def load_input(self)-> None:
        try:
            path = self.model.load_path()
            self.view.input_text(path) # type: ignore
        except Exception as e :
            logger.error(e)

    def click_hot_button(self)-> None:
        self.th.start()
        self.view.status_label_prepare()
        

    @Slot()
    def close_event(self)-> None:
        self.view.show_tray()
    
    #кнопка обзор  
    @Slot()  
    def push_search_button(self)-> None:
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
                self.model.save_path(self.folder)
                self.view.input_text(self.folder)
                logger.success("Папка выбрана путь сохранен в HKEY_CURRENT_USER\SOFTWARE\MyApp")

            else:
                logger.info("Папка отменина")
        except Exception as e:
            logger.error(f"Проблемма с кнопкой обзор {e}") 

    #срабатывает после того как в множесте 2 элемента
    #Обновляет кнопку,лейбл,и сохранеяет 
    @Slot(str)
    def update_btn_text(self,text:str)-> None:
        self.view.status_label_ready()
        self.view.update_btn(text)
        self.model.save_hot_key(text)

    @Slot()
    def load_hot_key(self)-> None:
        try:
            keys = self.model.load_hot_key()
            self.view.load_hot_key(keys)
        except:
            pass  
    #запускает выделение экрана
    @Slot()
    def run_screen(self)-> None:
        logger.info("Запуск облости захвата")
        self.screen.show()
        self.screen.clear()
    #Нажатие на скохранить в буффер
    @Slot(int, int, int, int) 
    def click_save_buffer(self,x1:int, y1:int,x2:int, y2:int)-> None:
        try:
            logger.info("Нажато сохрнаить в буфере")
            self.img = ImageGrab.grab(bbox=(x1, y1, x2,y2))
            self.output = io.BytesIO()
            self.img.convert('RGB').save(self.output, 'BMP')   
            data = self.output.getvalue()[14:]  # Убираем заголовок BMP
            self.output.close()
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard() 
            logger.success("Успешно сохраненно в буфер")                  
            self.screen._exit()
            #playsound('sound\sound.mp3')
            self.view.message_save_buffer()
        except Exception as e :
            if str(e) == "tile cannot extend outside image":
                self.screen.exit()
                self.screen.show_popup("Нельзя сделан скриншот пустого пространства")
                logger.info("Попытка сделать скриншот пустого окна")
            else:
                self.screen.exit()
                self.screen.show_popup(f"{e}")
                logger.error("Ошибка,не удалось сохранить в буффер")
    
    @Slot()
    def click_choose_color_button(self)-> None:
        try:
            dialog = QColorDialog()
            dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            dialog.setStyleSheet("""
                QColorDialog, QWidget {
                    background-color: white;
                    color: black;
                }
            """)
            logger.info("Открыто окно выбора цвета")
            dialog.setCurrentColor(QColor(Qt.black))
            
            if dialog.exec():
                color = dialog.selectedColor()
                if color.isValid():
                    self.color = color.name() 
                    self.paint.change_color(self.color)
                    logger.success(f"Выбран цвет {self.color}")
                    self.model.save_color(self.color)
            else:
                logger.info("Пользователь отменил выбор цвета")        
        except Exception as e:
            logger.error(f"Не получилось выбрать цвет {e}")
            self.screen.show_popup(f"Ошибка {e}")
    
    @Slot(int, int, int, int)
    def click_save_button(self,x1:int, y1:int,x2:int, y2:int)-> None:
        try:
            screenshot = ImageGrab.grab(bbox=(x1, y1,x2, y2))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_folder = self.view.return_input_text()
            filename = f"screenshot_{timestamp}.png"
            save_path = os.path.join(save_folder, filename)
            screenshot.save(save_path, "PNG")
        except FileNotFoundError :
            self.screen._exit()
            logger.error(f"произошла ошибка некоректный путь сохранения")
            self.screen.show_popup(f"Укажи корректный путь сохранения")
        except Exception as e :
            self.screen._exit()
            logger.error(f"произошла ошибка {e}")
            self.screen.show_popup(f"Ошибка {e}")
    
    #paint widghet 
    @Slot(int, int, int, int)        
    def create_paint(self,width:int,height:int,pos_x:int,pos_y:int)-> None:
        self.paint.start_paint(width,height,pos_x,pos_y)
    
    @Slot()
    def exit_paint(self)-> None:
        self.paint.close()

    @Slot()
    def clear_paint(self)-> None:
        self.paint.clear_paint() 

    @Slot(int)
    def set_brush_size(self,size:int)-> None:
        self.paint.set_size(size)
        self.model.save_pen_size(size)

    @Slot()
    def load_paint_setting(self)  -> None:
        size = self.model.load_pen_size()
        color = self.model.load_color()
        self.paint.defult_size(size)  
        self.screen.load_step(size)
        self.paint.load_color(color)

