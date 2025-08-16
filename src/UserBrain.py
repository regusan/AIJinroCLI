from Brain import Brain
from rich.console import Console

class UserBrain(Brain):
    """
    ユーザーが標準入力で操作するためのBrain
    """
    def __init__(self, systemInstruction:str="", modelVirsion:str="", thinking_budget:int=-1):
        """
        コンストラクタ
        rich.console.Consoleを初期化します。
        """
        self.console = Console()
        self.talkLog = []
        if systemInstruction:
            self.notice(f"システムインストラクションが設定されました:\n{systemInstruction}")

    def talk(self, text: str) -> str:
        """
        ユーザーにプロンプトを表示し、標準入力から文字列を受け取ります。

        Args:
            text (str): ユーザーへのプロンプトメッセージ。

        Returns:
            str: ユーザーが入力した文字列。
        """
        self.console.print(f"[bold green]>{text}[/bold green]", end="")
        response = self.console.input()
        self.talkLog.append({"role": "user", "parts": [{"text": text}]})
        self.talkLog.append({"role": "model", "parts": [{"text": response}]})
        return response

    def notice(self, text: str):
        """
        ユーザーに通知メッセージを表示します。

        Args:
            text (str): 表示する通知メッセージ。
        """
        #self.console.print(f"[bold yellow][Notice]: {text}[/bold yellow]")

    def select(self, text: str, options: list[str]) -> str:
        """
        ユーザーに選択肢を提示し、番号で選択させます。

        Args:
            text (str): ユーザーへのプロンプトメッセージ。
            options (list[str]): 選択肢のリスト。

        Returns:
            str: ユーザーが選択した項目。
        """
        self.console.print(f"[bold green]>{text}[/bold green]")
        for i, option in enumerate(options):
            self.console.print(f"  {i+1}: {option}")
        
        while True:
            try:
                choice_str = self.console.input(f"あなたの選択を番号で入力してください (1-{len(options)}): ")
                choice_index = int(choice_str) - 1
                if 0 <= choice_index < len(options):
                    selected_option = options[choice_index]
                    self.talkLog.append({"role": "user", "parts": [{"text": text}]})
                    self.talkLog.append({"role": "model", "parts": [{"text": selected_option}]})
                    return selected_option
                else:
                    self.console.print(f"[bold red]無効な選択です。1から{len(options)}の間で入力してください。[/bold red]")
            except ValueError:
                self.console.print("[bold red]無効な入力です。番号で入力してください。[/bold red]")

    def popLog(self, popCount: int = 1):
        """
        最新の会話ログを削除します。

        Args:
            popCount (int, optional): 削除する会話の数。デフォルトは1。
        """
        
        for _ in range(popCount):
            if self.talkLog:
                self.talkLog.pop()

    def UpdateSystemInstruction(self, systemInstruction: str):
        """
        システムインストラクションを更新し、ユーザーに通知します。
        Args:
            systemInstruction (str): 新しいシステムインストラクション。
        """
        #self.notice(f"システムインストラクションが更新されました:\n{systemInstruction}")

if __name__ == '__main__':
    # 実行例
    user_brain = UserBrain(systemInstruction="あなたは人狼ゲームの参加者です。")

    user_brain.notice("ゲームが開始されました。あなたは村人です。")

    opinion = user_brain.talk("最初の発言をどうぞ: ")
    print(f"あなたが入力した発言: {opinion}")

    players = ["Player1", "Player2", "Player3"]
    vote = user_brain.select("誰に投票しますか？", players)
    print(f"あなたが投票した相手: {vote}")

    print("会話ログ:")
    print(user_brain.talkLog)

    user_brain.popLog()
    print("popLog()後の会話ログ:")
    print(user_brain.talkLog)