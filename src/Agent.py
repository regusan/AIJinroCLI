from Brain import Brain
from Role import Role
class Agent:
    """
    ロールを演じるエージェントのクラス
    """
    def __init__(self, name: str, brain: Brain, role:Role, persona: str = ""):
        """
        コンストラクタ
        """
        self.name: str = name
        self.role: Role = role
        self.persona: str = persona
        self.brain: Brain = brain
    
    def __str__(self):
        return f"[cyan]{self.name}[/cyan]([yellow]{self.role}[/yellow])"


    def notice(self, text: str):
        self.brain.notice(text)
    def talk(self, text: str):
        return  self.brain.talk(text)
    def select(self,text:str, options:list[str]):
        return self.brain.select(text, options)

