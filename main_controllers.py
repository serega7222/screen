#main_controllers.py
from log import logger
from PySide6.QtWidgets import QFileDialog ,QColorDialog                        
from model import *
from PySide6.QtGui import QColor
from PIL import  ImageGrab
import io
from datetime import datetime
import os
from PySide6.QtCore import Qt,  QThread, Signal,Slot
import win32clipboard
from view.main_screen import MainScreen
from view.selector_screen import ScreenSelector
from view.paint_screen import PainterWidget
from controllers.hot_key  import HotKey 
from controllers.main_screen_controller import MainScreenController


class MainController:
    def __init__(self)-> None:
        self.model = Model()
        self.main_screen = MainScreen()
        self.th = HotKey()
        self.main_screen_controller = MainScreenController(self.main_screen,self.th,self.model  )
        self.screen = ScreenSelector()
        self.paint = PainterWidget()
        self.th.check_press_hot_key()
        self.load_input()
        self.load_hot_key()
        #подключить сигналы
        self.connect_signal()
        
    #подключает сигналы          
    def connect_signal(self)-> None:
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
            self.main_screen.input_text(path) # type: ignore
        except Exception as e :
            logger.error(e)



    #срабатывает после того как в множесте 2 элемента
    #Обновляет кнопку,лейбл,и сохранеяет 
    @Slot(str)
    def update_btn_text(self,text:str)-> None:
        self.main_screen.status_label_ready()
        self.main_screen.update_btn(text)
        self.model.save_hot_key(text)

    @Slot()
    def load_hot_key(self)-> None:
        try:
            keys = self.model.load_hot_key()
            self.main_screen.load_hot_key(keys)
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
            self.main_screen.message_save_buffer()
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
            save_folder = self.main_screen.return_input_text()
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

