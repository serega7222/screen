#controllers/tool_panel_controller.py
from view.tool_panel import ToolPanel

class ToolPanelController():
    def __init__(self,tool_panel:ToolPanel)-> None:
        self.tool_panel = tool_panel