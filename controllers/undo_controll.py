#controllers\undo_controll.py
from view.screen_selector import ScreenSelector
from PySide6.QtCore import  Slot
from view.paint import PainterWidget
from utils.log import logger

class UndoControl():
    """Отвечает за отмену предыдущих действий,так же вызывает функцию рисования"""
    def __init__(self,screen : ScreenSelector,paint:PainterWidget)-> None:
        self.screen = screen
        self.paint = paint
        self.lst_point = []
        self._connect_signals()

    def _connect_signals(self) -> None:  
        self.paint.pen_move_signal.connect(self._pen_move)
        self.paint.pen_is_up_signal.connect(self._pen_is_up)
        self.paint.clear_lst_signal.connect(self._click_clear)
        self.screen.choose_clean_signal.connect(self._click_clear)
        self.screen.prev_signal.connect(self._click_prev)

    def _click_next(self)  -> None: 
        pass

    def _click_prev(self)-> None: 
        """Отменяет предыдущие действие ,удаляя из списка координаты ,
        вызывает при получении сигнала из  #view/selector_screen.py
        после удаления элемента вызывает отрисовку по оставшимся элементам списка ,отрисовка находится в файле view/paint.py функция draw"""
        if len(self.lst_point) > 0:
            self.lst_point.pop()
            self.paint.clear_paint()
            self.paint.draw(self.lst_point)
        else:
            logger.info("Достигнут конец списка")

    def _click_clear(self)-> None: 
        """Удаляет все элементы в списке ,так же очищает полотно от всех рисунков ,
        отчистка полотная находиться в #view/paint.py  функция clear_paint """
        self.lst_point.clear()
        self.paint.clear_paint()
    
    @Slot(object,object,object,int,int)
    def _pen_move(self,*args)-> None:
        """Функция срабатывает когда получает сигнал о том что левая клавиши мыши нажата и мышка находится в движении 
        сигнал идет из файла view/paint.py функции mouseMoveEvent
            args : начальная позиция курсора ,конечная позиция курсора,цвет линии ,толщина линии, прозрачность линии
        
        """
        logger.info("Ручку ведут по полотну")
        
        self.lst_point.append((args))
        self.paint.draw(self.lst_point)
        

    @Slot()
    def _pen_is_up(self)-> None:
        """срабатывает при получении сигнала что левая клавиша мышки поднята сигнал идет из файла view/paint.py функции mouseReleaseEvent"""
        logger.info("Ручка оторвана от полотна")
        #self.paint.draw(lines = None)
        