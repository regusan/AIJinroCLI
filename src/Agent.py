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
        first_line_persona = self.persona.splitlines()[0] if self.persona else ''
        return f"[cyan]{self.name}[/cyan]([yellow]{self.role}[/yellow], [yellow]{first_line_persona}[/yellow], [yellow]{self.brain.modelVirsion}[/yellow])"


    def notice(self, text: str):
        self.brain.notice(text)
    def talk(self, text: str):
        return  self.brain.talk(text)
    def select(self,text:str, options:list[str]):
        return self.brain.select(text, options)

if __name__ == "__main__":
    # Agentクラスの使用例

    # テスト用のダミーBrainクラス
    # Agentの__str__はbrain.modelVirsionにしかアクセスしないため、
    # 完全な実装は不要
    class DummyBrain(Brain):
        def __init__(self, modelVirsion="dummy-v1"):
            self.modelVirsion = modelVirsion
        def talk(self, text: str) -> str: return ""
        def notice(self, text: str): pass
        def select(self, text: str, options: list[str]) -> str: return ""
        def popLog(self, popCount: int = 1): pass
        def UpdateSystemInstruction(self, systemInstruction: str): pass

    # ダミーの依存オブジェクトを作成
    dummy_brain = DummyBrain()
    dummy_role = Role(name="村人", prompt="あなたは村人です。特別な能力はありません。")

    # エージェントを作成
    agent1 = Agent(
        name="エージェントA",
        brain=dummy_brain,
        role=dummy_role,
        persona="""
元気で活発な性格。
思ったことはすぐ口に出す。
"""
    )

    agent2 = Agent(
        name="エージェントB",
        brain=dummy_brain,
        role=dummy_role,
        persona="冷静沈着な性格。"
    )

    # __str__メソッドの呼び出し（print関数が内部で呼び出す）
    from rich.console import Console
    console = Console()
    console.print(agent1)
    console.print(agent2)