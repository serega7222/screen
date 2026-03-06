#controllers\undo_controll.py
from view.screen_selector import ScreenSelector
from PySide6.QtCore import  Slot
from view.paint import PainterWidget
from utils.log import logger

class UndoControl():
    def __init__(self,sceen : ScreenSelector,paint:PainterWidget)-> None:
        self.screen = sceen
        self.paint = paint
        self.lst_point = []
        self._coonect_signal()

    def _coonect_signal (self) -> None:  
        self.paint.pen_move_signal.connect(self._pen_move)
        self.paint.pen_is_up_signal.connect(self._pen_is_up)
        self.paint.clear_lst_signal.connect(self._click_clear)
        self.screen.choose_clean_signal.connect(self._click_clear)
        self.screen.prev_signal.connect(self._click_prev)

    def _click_next(self)  -> None: 
        pass

    def _click_prev(self)-> None: 
        if len(self.lst_point) > 0:
            self.lst_point.pop()
            self.paint.clear_paint()
            self.paint.draw(self.lst_point)
        else:
            logger.info("Достигнут конец списка")

    def _click_clear(self)-> None: 
        self.lst_point.clear()
        self.paint.clear_paint()
    
    @Slot(object,object,object,int,int)
    def _pen_move(self,*args)-> None:
        """Функция получает значения из paint.py координаты ,цвет ,толщену и прозрачность"""
        logger.info("Ручку ведут по полотну")
        
        self.lst_point.append((args))
        self.paint.draw(self.lst_point)
        

    @Slot()
    def _pen_is_up(self)-> None:
        logger.info("Ручка оторвана от полотна")
        #self.paint.draw(lines = None)
        