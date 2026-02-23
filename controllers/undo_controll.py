#controllers\undo_controll.py
from view.screen_selector import ScreenSelector
from PySide6.QtCore import  Slot
from view.paint import PainterWidget

class UndoControl():
    def __init__(self,sceen : ScreenSelector,paint:PainterWidget)-> None:
        self.screen = sceen
        self.screen .choose_clean_signal.connect(self.clear_paint)
        self.screen.next_signal.connect(self.click_next)
        self.screen.prev_signal.connect(self.click_prev)
        self.paint = paint
        self.paint.draw_signal.connect(self.draw_signal)
        self.lines = [] 
        self.counter = 0
        
    @Slot()
    def clear_paint(self):
        self.paint.clear_paint()
        
    @Slot()
    def click_next(self):
        print("sss")

    @Slot()
    def click_prev(self):
        if len(self.lines) >= 5:
            # Удаляем 5 последних линий
            for i in range(5):
                self.lines.pop()
           
        else:
            # Удаляем все линии (очищаем)
            self.lines.clear()

        self.clear_paint()
        self.paint.draw(self.lines)     

    @Slot(object,object,object,int,int)
    def draw_signal(self,current,previos,color,width,alpha):
        self.lines.append((current,previos,color,width,alpha))
        self.clear_paint()
        self.paint.draw(self.lines)

        