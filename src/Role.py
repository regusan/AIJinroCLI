class Role:
    """
    役職の定義を保持するクラス
    """
    def __init__(self, name: str, prompt: str):
        """
        コンストラクタ

        Args:
            name (str): 役職名
            prompt (str): 役職の振る舞いを定義するプロンプト
        """
        self.name: str = name
        self.prompt: str = prompt

    def __str__(self):
        return self.name
