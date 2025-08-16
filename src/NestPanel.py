from rich.panel import Panel
from rich.console import Group

class NestPanel:
    def __init__(self, title:str):
        self.childPanels:list[Panel] = []
        self.panelGroupe:Group = Group(*self.childPanels) 
        self.parentPanel:Panel = Panel(
            self.panelGroupe,
            title=title,
            border_style="blue",
        )
    
    def append(self, panel):
        self.childPanels.append(panel)
        self.parentPanel.renderable = Group(*self.childPanels)