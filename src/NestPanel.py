
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.console import Group
from rich.rule import Rule

class NestPanel:
    def __init__(self, title):
        self.childPanels = []
        self.panelGroupe = Group(*self.childPanels) 
        self.parentPanel = Panel(
            self.panelGroupe,
            title=title,
            border_style="blue",
        )
    
    def append(self, panel):
        self.childPanels.append(panel)
        self.parentPanel.renderable = Group(*self.childPanels)