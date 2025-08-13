from Brain import Brain
from rich.console import Console

class GeminiBrain(Brain):
    """
    GeminiBrainのGemini実装
    """
    def __init__(self):
        self.console = Console()
        self.context: str = ""

    def talk(self, text: str) -> str:
        """
        会話を行い、コンテキストを更新する
        """
        self.context += f"\n[User]: {text}"
        # TODO: ここで実際にGemini APIを呼び出す
        response = f"AIの応答(ダミー): 入力は「{text}」でした。"
        self.context += f"\n[AI]: {response}"
        return response

    def notice(self, text: str):
        """
        通知を受け取り、コンテキストに追加する
        """
        self.console.print(f"[dim]通知({id(self)}): {text}[/dim]")
        self.context += f"\n[Notice]: {text}"
