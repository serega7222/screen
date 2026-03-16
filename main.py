#main.py
import sys
from PySide6.QtWidgets import QApplication
from dataclasses import dataclass

#Представление
from view.main_screen import MainScreen
from view.screen_selector import ScreenSelector
from view.tray import Tray
from view.paint import PainterWidget
from view.tool_panel import ToolPanel
#Модель
from model.model import Model
#Контроллеры
from controllers.main_screen_control import MainScreenControl
from controllers.hot_key_control import WatchPress
from controllers.save_control import SaveControl
from controllers.color_controller import ColorPickerController
from controllers.undo_control import UndoControl
from controllers.tool_panel_controller import ToolPanelController

@dataclass
class AppModels:
    """Контейнер для всех компонентов приложения, чтобы не умерли"""
    save_control: SaveControl
    color_controller: ColorPickerController
    undo_control: UndoControl
    main_control: MainScreenControl
    tool_control: ToolPanelController
    watcher: WatchPress
    model: Model
    main_window: MainScreen
    paint: PainterWidget
    tool_panel: ToolPanel
    screen_selector: ScreenSelector
    tray: Tray


def setup_application(app: QApplication) -> AppModels:
    """Инициализирует и возвращает модели приложения"""
    
    # Стили
    style_file = "static/style.css" 
    with open(style_file, "r", encoding="UTF-8") as file:
        app.setStyleSheet(file.read())    
    
    # Модель
    model = Model()   
    
    # Представления
    main = MainScreen()
    paint = PainterWidget(model)
    tool_panel = ToolPanel(paint, model)
    screen_selector = ScreenSelector(paint, model, tool_panel)
    tray = Tray(main)
    
    # Служебные
    watcher = WatchPress()
    
    # Контроллеры 
    save_control = SaveControl(screen_selector, tray, main, tool_panel)
    color_controller = ColorPickerController(screen_selector, paint, model, tool_panel) 
    undo_control = UndoControl(screen_selector, paint, tool_panel)
    tool_panel_controller = ToolPanelController(tool_panel)
    # Горячие клавиши 
    watcher.check_press_hot_key()
    
    main_control = MainScreenControl(main, model, watcher, screen_selector)
    
    # Собираем всё в модуле и возвращаем
    return AppModels(
        save_control=save_control,
        color_controller=color_controller,
        undo_control=undo_control,
        main_control=main_control,
        tool_control=tool_panel_controller,
        watcher=watcher,
        model=model,
        main_window=main,
        paint=paint,
        tool_panel=tool_panel,
        screen_selector=screen_selector,
        tray=tray
    )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = setup_application(app)  
    sys.exit(app.exec())