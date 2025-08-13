from Agent import Agent
from GeminiBrain import GeminiBrain
from Brain import Brain
from Role import Role
from rich.console import Console
from rich.panel import Panel
import random
from typing import List, Tuple, Dict

gameRule = """
# ゲーム名
人狼ゲーム

# ルール
- 人狼陣営と市民陣営に分かれ、各陣営の勝利を目指す。
- 人狼陣営の勝利条件は、市民陣営のと人狼陣営を同数いかにすること。
- 市民陣営の勝利条件は、人狼陣営を全滅させること。

# 投票ルール
- 一人1票投票できる。
- 最も投票数の多い人は処刑される。同数ならだれも処刑されない。
- 処刑されると、以降の議論では何も発言できなくなり、行動もできなくなり、投票権も失う。

# 役職
## 市民
- 市民陣営
## 占い師
- 市民陣営
- 毎晩、一人のプレイヤーの役職を知ることができる。占い結果は本人が直接他の人に伝えることで伝えられる。ゲームマスターは直接通知しない。
## 人狼
- 人狼陣営
- 毎晩、一人市民を襲撃できる。

"""

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
        self.publicGameState: list[str] =[]
        self.privateGameState: list[str] =[]
        self.privateGameLog: list[str] =[]
        self.publicGameLog: list[str] =[]
        self.console = Console()

        startupMSG = """
あなたは人狼ゲームのゲームマスターです。
あなたの仕事は、各エージェント(プレイヤー)の応答を記録し、ゲームの状態を更新することです。
ゲームの状態はあなたのコンテキストによって管理されます。
"""
        self.brain.notice(startupMSG)
        self.brain.notice(f"ゲームルール: {gameRule}")

    def begin(self):
        """
        ゲームの開始
        """
        self.console.print(Panel("[bold cyan]AI人狼ゲームへようこそ！[/bold cyan]", title="ゲーム開始"))

        self.agents = [Agent(f"エージェント{i+1}", GeminiBrain()) for i in range(len(self.roles))]

        for i, agent in enumerate(self.agents):
            agent.role = self.roles[i].name
            startupmsg = f"""
あなたはオンライン人狼ゲームの参加者です。
ほかのプレイヤーは人間であり、あなたがAIであることは秘匿されています。
そのため人間らしいふるまいを行ってください。
また、これがテキストベースのゲームであることを考慮してください。つまり、あなたの得意な整形された文章は不自然ですので注意してください。
また、回答時には括弧を付けたり、発言""のようにしないで、平文でお願いします。
f"ただいまより人狼ゲームを開始します。あなたの名前は、{agent.name}です。あなたの役職は{agent.role}です。プロンプト: {self.roles[i].prompt}"
参加者は{", ".join([agent.name for agent in self.agents])}です。
"""
            agent.notice(startupmsg)
            agent.notice(f"ゲームのルール: {gameRule}")

            

        agentRoleMap = {agent.name: agent.role for agent in self.agents}
        agentRoleMapStr = ", ".join([f"{name}: {role}" for name, role in agentRoleMap.items()])
        self.brain.notice("各エージェントの役職は"+agentRoleMapStr)

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
                tmp = agent.talk("[ゲームマスター]あなたの役職に基づいた最適な行動を推測してください")
                self.console.print(f"    [dim]{agent.name}の応答:[/dim] " +  tmp)
                action = agent.talk("[ゲームマスター]行動を簡潔に述べてください。")
                self.console.print(f"    [dim]{agent.name}の応答:[/dim] " +  action)
                actionresult = self.brain.talk(f"夜の行動: {agent.name}が「{action}」と行動しました。もし、結果がある行動(例：占いの結果)なら通知してください。なければ何も応答しないで。")
                agent.notice("結果のある行動の場合は結果が入ります。:"+actionresult)


            self.console.print("夜の行動が終了しました。")

            # 夜の行動結果を通知
            # TODO: 実際の襲撃結果などを反映させる
            lastNightExplain = self.brain.talk("集計した昨晩の行動による結果を簡潔に教えてください。")
            notification = lastNightExplain
            self.publicGameState += f"\n{day}日目夜: {notification}"
            self.console.print(Panel(self.publicGameState, title="公開情報"))

            self.noticeBCast(notification, self.agents)

            if self._check_game_end(): break

            # --- 昼のターン ---
            self.console.print(Panel("[bold yellow]昼になりました。議論を開始してください。[/bold yellow]", title=f"{day}日目 - 昼"))
            self.conversation(talktheme="昨晩の出来事と、誰が人狼だと思うかについて", agents=self.agents, loopcount=1)


            # --- 投票 ---
            self.console.print(Panel("[bold red]追放投票の時間です。[/bold red]", title=f"{day}日目 - 投票"))
            voteResult = ""
            for agent in self.agents:
                voteResult+=f"{agent.name}:{agent.talk("[ゲームマスター]だれに投票するか教えてください。無投票も可能です。名前のみ述べてください。それ以外は出力しないで。")}\n"
            
            self.console.print("投票が終了しました。")
            self.brain.talk(f"誰が追放されるか教えて。投票結果{voteResult}から、最も投票数の多い人を選んでください。もし同数なら無効投票とします。")
            
            self.noticeBCast(f"投票結果:\n{voteResult}", self.agents)
            self.console.print(Panel(voteResult, title="投票結果"))
            if self._check_game_end(): break
            
            day += 1
            


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
            conversation_log += header + "\n"
            for agent in agents:
                response =agent.talk(conversation_log)
                self.console.print(f"[cyan]{agent.name}:[/cyan] {response}")
                conversation_log += f"{agent.name}: {response}\n"

        self.console.print(Panel("会話終了", style="bold green"))
        return conversation_log
    def noticeBCast(self, bcastText:str, agents:list[Agent]):
        """
        全エージェントにブロードキャストメッセージを送信する
        """
        self.console.print(f"[bold blue]ブロードキャスト: {bcastText}[/bold blue]")
        for agent in agents:
            agent.notice(bcastText)


    def _check_game_end(self) -> bool:
        """
        ゲームの終了条件を確認する
        """
        endTxt = self.brain.talk("現状で、ゲームの終了条件に合致しますか？合致するなら、'終了'、しないなら'継続'を出力してください。プログラムで処理するため、それ以外は何も出力しないで。")
        return endTxt == "終了"