from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QFileDialog, QSystemTrayIcon, QMenu,QCheckBox,QComboBox
from PySide6.QtWidgets import QApplication, QWidget, QRubberBand
from PySide6.QtCore import Qt, QRect, QSize, QThread, Signal, QObject,QSettings
from PySide6.QtGui import QKeySequence, QShortcut, QIcon, QAction ,QKeyEvent
import keyboard
import threading



class HotkeyThread(QThread):
    hotkey_triggered = Signal()
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        # Регистрируем глобальную горячую клавишу Ctrl+S
        keyboard.add_hotkey('ctrl+s', self.trigger_hotkey)
        # Блокируем поток, пока не будет остановлен
        keyboard.wait()
        
    def trigger_hotkey(self):
        self.hotkey_triggered.emit()
        
    def stop(self):
        self.running = False
        keyboard.unhook_all()

class ScreenSelector(QWidget):
    def __init__(self):
        super().__init__()
        # Окно на весь экран, без рамок, поверх остальных
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.setWindowOpacity(0.3) # Полупрозрачность для видимости экрана
        self.setWindowState(Qt.WindowFullScreen)
        
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = None

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubber_band.setGeometry(QRect(self.origin, QSize()))
        self.rubber_band.show()

    def mouseMoveEvent(self, event):
        if self.origin:
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        selected_rect = self.rubber_band.geometry()
        print(f"Выбранная область: {selected_rect}")
        self.rubber_band.hide()
        self.close() # Закрыть окно после выбора



class View(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setFixedSize(500, 400)
        self.setWindowTitle("Скриншотер экрана")
        self.load_ui()
        self.load_trey() 
    def load_ui(self):
        window_shortcut = QShortcut(QKeySequence("Ctrl+S"),self)
        window_shortcut.activated.connect(self.controller.run_screen)

        #Кнопки и интерфейсы
        self.lable_save = QLabel("Куда сохранить",self)
        self.save_inp = QLineEdit(self)

        self.save_inp.move(100,2)
        self.save_inp.resize(300,25)

        self.search_button = QPushButton("Обзор",self)
        self.search_button.move(400,0)
        self.search_button.clicked.connect(self.controller.push_search)
        self.lable_hot_key = QLabel("Сделать скрин",self)
        self.lable_hot_key.move(0,50)
        self.hot_key_button = QPushButton("Ctrl+S",self)
        self.hot_key_button.move(100,50)

        self.lable_save_format = QLabel("Формат ",self)
        self.lable_save_format.move(0,100)        
        self.lable_save_format.resize(150,25)

        self.combo = QComboBox(self)
        self.items = ["PNG","JPEG","JPG"]
        self.combo.addItems(self.items)
        self.combo.move(100,100)  
        self.combo.currentTextChanged.connect(self.controller.change_box)

    def load_trey(self):
        # Создаем иконку трея
        self.tray_icon = QSystemTrayIcon(self)
        
        # УСТАНАВЛИВАЕМ ИКОНКУ - это обязательно!
        self.tray_icon.setIcon(self.style().standardIcon(
            self.style().StandardPixmap.SP_ComputerIcon))
        
        self.tray_icon.show()

        self.trey_menu = QMenu()

        #Показать кнопка
        self.button_show = QAction("Показать",self)
        self.button_show.triggered.connect(self.controller.button_show_clicked)
        self.trey_menu.addAction(self.button_show)

        self.trey_menu.addSeparator()

        #Кнопка выйти
        self.button_exit = QAction("Выйти",self)
        self.button_exit.triggered.connect(self.controller.button_exit_clicked)
        self.trey_menu.addAction(self.button_exit)

        self.tray_icon.setContextMenu(self.trey_menu)
        # Cообщение
        self.tray_icon.showMessage(
            "Приложение запущено",
            "Программа работает в системном трее",
            QSystemTrayIcon.Information,
            2000
        )

    def closeEvent(self, event):
        # Вместо закрытия - сворачиваем в трей
        print("sss")                  


        
class Controller:
    def __init__(self):
        self.view = View(self)
        self.view.show()
        self.settings = QSettings("MyApp", "Screenshotter")
        self.load_setting()
    def run_screen(self):
        self.screen = ScreenSelector()
        self.screen.show()

    def push_search(self):
        folder = QFileDialog.getExistingDirectory(
            self.view,  # родительское окно
            "Выберите папку",  # заголовок
            "",  # начальная директория
            QFileDialog.Option.ShowDirsOnly  # опции
        )  

        if folder:
            self.view.save_inp.setText(folder)
            self.settings.setValue("save_path", folder)

    def load_setting(self):
        path = self.settings.value("save_path", )
        format = self.settings.value("format", )
        if path :
            self.view.save_inp.setText(path)
        if format :
            self.view.combo.setCurrentText(format)
    def change_box(self,text):
        self.settings.setValue("format", text)

    def button_show_clicked(self):
        print("НАжата кнопка показать")  

    def button_exit_clicked(self):
        print("Нажат кнока выйти")
   
if __name__ == "__main__":
    app = QApplication([])
    controller = Controller()
    hotkey_thread = HotkeyThread()
    hotkey_thread.hotkey_triggered.connect(controller.run_screen)
    hotkey_thread.start()
    
    app.exec()    