from Agent import Agent
from GeminiBrain import GeminiBrain
from Brain import Brain
from Role import Role
from rich.console import Console
from rich.panel import Panel
import random
from typing import List, Tuple, Dict

class GameMaster:
    """
    ゲームの進行を管理するクラス
    """
    def __init__(self, roles: list[Role]):
        """
        コンストラクタ
        """
        self.brain: Brain = GeminiBrain()
        self.agents: list[Agent] = []
        self.roles: list[Role] = roles
        self.publicGameState: list[str] = ""
        self.privateGameState: list[str] = ""
        self.console = Console()

    def begin(self):
        """
        ゲームの開始
        """
        self.console.print(Panel("[bold cyan]AI人狼ゲームへようこそ！[/bold cyan]", title="ゲーム開始"))

        self.agents = [Agent(f"エージェント{i+1}", GeminiBrain()) for i in range(len(self.roles))]

        shuffled_roles = list(self.roles)
        random.shuffle(shuffled_roles)
        for i, agent in enumerate(self.agents):
            agent.role = shuffled_roles[i].name
            agent.notice(f"あなたの役職は{agent.role}です。プロンプト: {shuffled_roles[i].prompt}")

        self.console.print("各エージェントに役職を割り振りました。")
        self.publicGameState = f"参加者: {len(self.agents)}名"
        self.console.print(Panel(self.publicGameState, title="公開情報"))

        agentInfo = "\n".join([f"{agent.name}: {agent.role}" for agent in self.agents])
        self.privateGameState.append(agentInfo)
        self.console.print(Panel(agentInfo, title="秘密情報", style="bold red"))


    def gameloop(self):
        """
        ゲームのメインループ
        """
        self.console.print(Panel("[bold magenta]ゲームループ開始[/bold magenta]"))
        day = 1
        while not self._check_game_end():
            self.console.print(Panel(f"[bold]====== {day}日目 ======[/bold]", expand=False))

            # --- 夜のターン ---
            self.console.print(Panel("[bold blue]夜が来ました。各役職は行動してください。[/bold blue]", title=f"{day}日目 - 夜"))
            # TODO: 各役職の行動を実装
            for agent in self.agents:
                self.console.print(f"  [bold]{agent.name}[/bold] (役職: {agent.role}) が行動中...")
                agent.talk("あなたの役職に基づいた最適な行動を推測してください")
                result = agent.talk("先の行動に基づいた、行動を教えてください")
                

            self.console.print("夜の行動が終了しました。")

            # 夜の行動結果を通知
            # TODO: 実際の襲撃結果などを反映させる
            notification = "昨晩は誰も死にませんでした。"
            self.publicGameState += f"\n{day}日目夜: {notification}"
            for agent in self.agents:
                agent.notice(notification)

            if self._check_game_end(): break

            # --- 昼のターン ---
            self.console.print(Panel("[bold yellow]昼になりました。議論を開始してください。[/bold yellow]", title=f"{day}日目 - 昼"))
            self.conversation(talktheme="昨晩の出来事と、誰が人狼だと思うかについて", agents=self.agents, loopcount=2)
            
            # --- 投票 ---
            self.console.print(Panel("[bold red]追放投票の時間です。[/bold red]", title=f"{day}日目 - 投票"))
            # TODO: 投票処理を実装
            self.console.print("投票が終了しました。")

            if self._check_game_end(): break
            
            day += 1
            # 現状はループが無限に続くため、仮でブレーク
            break


    def end(self):
        """
        ゲームの終了
        """
        self.console.print(Panel("[bold green]ゲーム終了！[/bold green]", title="ゲーム終了"))
        # TODO: 勝利陣営の判定と表示
        
        self.console.print("感想戦を開始します。")
        # TODO: 感想戦(conversation)を実装

        # デバッグ用にエージェント0の最終コンテキストを表示
        if self.agents:
            final_context = self.agents[0].brain.context
            self.console.print(Panel(final_context, title=f"{self.agents[0].name}の最終コンテキスト", style="bold yellow"))


    def conversation(self, talktheme: str, agents: list[Agent], loopcount: int) -> str:
        """
        会話のサブルーチン
        """
        self.console.print(Panel(f"会話テーマ: {talktheme}", title="会話開始", style="bold green"))
        
        conversation_log = f"テーマ: {talktheme}\n"
        
        for i in range(loopcount):
            header = f"--- 議論ターン {i+1} ---"
            self.console.print(header)
            for agent in agents:
                response =agent.talk(header + "\n" + conversation_log)
                self.console.print(f"[cyan]{agent.name}:[/cyan] {response}")
                conversation_log += f"{agent.name}: {response}\n"

        self.console.print(Panel("会話終了", style="bold green"))
        return conversation_log

    def _check_game_end(self) -> bool:
        """
        ゲームの終了条件を確認する
        """
        # TODO: ゲーム終了ロジックを実装
        # 例: 人狼が全滅 or 人狼と市民が同数
        return False