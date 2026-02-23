#main.py
import sys
from PySide6.QtWidgets import QApplication
from view.main_screen import MainScreen
from view.screen_selector import ScreenSelector
from view.tray import Trey
from view.paint import PainterWidget
from controllers.main_screen_control import MainScreenControl
from controllers.hot_key_control import WatchPress
from controllers.buffer_save_control import BufferSave
from controllers.local_save_control import LocalSave
from controllers.pen_controller import PenController
from controllers.marker_control import MarkerControl
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
    screen_selector = ScreenSelector(paint,model)
    trey = Trey(main)
    buffer_save = BufferSave(screen_selector,trey)
    local_save = LocalSave(screen_selector,trey,main)
    pen = PenController(screen_selector,paint,model)
    marker = MarkerControl(screen_selector,paint,model)
    undo_controll = UndoControl(screen_selector,paint)
    watcher.check_press_hot_key()
    main_screen_controll = MainScreenControl(main,model,watcher,screen_selector)
    
    #app.setQuitOnLastWindowClosed(False)
    sys.exit(app.exec())