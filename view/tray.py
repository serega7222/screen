#view/tray.py
from view.main_screen import MainScreen
from PySide6.QtWidgets import QSystemTrayIcon
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QLineEdit,
                                 QSystemTrayIcon, QMenu,QGridLayout)
from PySide6.QtGui import ( QAction ,QCloseEvent)
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QObject

class Tray(QObject):
    def __init__(self, main_window: MainScreen)-> None:
        super().__init__(main_window)  
        self.main_window = main_window
        self.tray_icon = None
        self.init_tray()
        
        
    def init_tray(self) -> None:
        """Создает объект для системного трея"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Устанавливаем иконку из главного окна
        icon = self.main_window.style().standardIcon(
            self.main_window.style().StandardPixmap.SP_ComputerIcon
        )
        self.tray_icon.setIcon(icon)
        
    def show_tray(self) -> None:
        """Показывает трей с меню"""
        # Меню трея
        self.tray_menu = QMenu()
        
        self.show_action = QAction("Показать", self)
        self.quit_action = QAction("Выход", self)
        
        # Подключаем сигналы к главному окну
        self.show_action.triggered.connect(self.main_window.showNormal)
        self.quit_action.triggered.connect(self.quit_application)
        
        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addAction(self.quit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        
        # Показываем приветственное сообщение
        self.tray_icon.showMessage(
            "Приложение свернулось в трей",
            "Для скриншота нажми горячие клавиши",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def quit_application(self)-> None:
        """Корректное завершение приложения"""
        # Скрываем трей перед выходом
        if self.tray_icon:
            self.tray_icon.hide()
        QApplication.instance().quit()

    def message_save_buffer(self)-> None:
        """Выходит при сохранении в буфер обмена"""
        self.tray_icon.show()
        self.tray_icon.showMessage(
        "Успешно",
        "Сохранено в буфер обмена",
        QSystemTrayIcon.MessageIcon.Information,
        2000
    )     

    def message_save_local(self,path)-> None:
        """Появляется при сохранение локально"""
        self.tray_icon.show()
        self.tray_icon.showMessage(
        "Успешно",
        f"Сохранено локально по пути {path}",
        QSystemTrayIcon.MessageIcon.Information,
        2000
    )     

                