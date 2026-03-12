#main.py
import sys
from PySide6.QtWidgets import QApplication
from view.main_screen import MainScreen
from view.screen_selector import ScreenSelector
from view.tray import Tray
from view.paint import PainterWidget
from view.tool_panel import ToolPanel
from controllers.main_screen_control import MainScreenControl
from controllers.hot_key_control import WatchPress
from controllers.save_controll import SaveControll

from controllers.color_controller import ColorPickerController
from controllers.undo_controll import UndoControl
from model.model import Model

if __name__ == "__main__":
    app = QApplication(sys.argv)
    style_file = "static/style.css" 
    with open(style_file, "r",encoding="UTF-8") as file:
        app.setStyleSheet(file.read())        

    main = MainScreen()
    model = Model()
    watcher = WatchPress()
    paint = PainterWidget(model)
    tool_panel = ToolPanel(paint ,model)
    screen_selector = ScreenSelector(paint,model,tool_panel)
    trey = Tray(main)
    save_controll = SaveControll(screen_selector,trey,main,tool_panel)
    color_picker_controler = ColorPickerController(screen_selector,paint,model,tool_panel) 
    undo_controll = UndoControl(screen_selector,paint,tool_panel)
    watcher.check_press_hot_key()
    main_screen_controll = MainScreenControl(main,model,watcher,screen_selector)
    
    #app.setQuitOnLastWindowClosed(False)
    sys.exit(app.exec())