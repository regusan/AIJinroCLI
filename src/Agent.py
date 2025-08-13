from Brain import Brain

class Agent:
    """
    ロールを演じるエージェントのクラス
    """
    def __init__(self, name: str, brain: Brain, persona: str = ""):
        """
        コンストラクタ
        """
        self.name: str = name
        self.role: str = ""
        self.persona: str = persona
        self.brain: Brain = brain

    def notice(self, text: str):
        self.brain.notice(text)

