from Agent import Agent
from GeminiBrain import GeminiBrain
from Brain import Brain
from Role import Role
from rich.console import Console
from rich.panel import Panel

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.console import Group
from rich.rule import Rule
import random
from typing import List, Tuple, Dict

from NestPanel import NestPanel

gameRule = """
# ゲーム名
人狼ゲーム

# ルール
- 人狼陣営と市民陣営に分かれ、各陣営の勝利を目指す。
- 人狼陣営の勝利条件は、市民陣営のと人狼陣営を同数以下にすること。
- 市民陣営の勝利条件は、人狼陣営を全滅させること。
- 処刑・狼による襲撃などで死亡した場合、以降の議論では何も発言できなくなり、行動もできなくなり、投票権も失う。
- エージェントは役職を騙ることも可能です。

# UI説明
## メッセージ説明
- [GM]はゲームマスターからのメッセージであることを示しています。
- [Username]はUsernameの発言であることを示します。
- [Notice]は通知です。返信はできません。あなたに質問が求められた際にまとめて複数スタック送られることもあります。

# 投票ルール
- 一人1票投票できる。
- 最も投票数の多い人は処刑される。同数ならだれも処刑されない。

# 役職
## 市民
- 市民陣営
### 夜間行動
- 無し

## 占い師
- 市民陣営
### 夜間行動
- 選択したプレイヤー1人の役職を知ることができる。占い行動を行う場合は名前を明示してください。
- 行動発言フォーマット:"エージェント名"
- 公開情報:無し
- 本人への通知内容:占い結果
#### 例:
GMからの質問"[GM]誰を占いますか？"
占い師の応答"Username"

## 人狼
- 人狼陣営
### 夜間行動
- 任意の市民を一人襲撃できる。襲撃する場合は名前を明示してください。
- 行動発言フォーマット:"エージェント名"
- 公開情報:犠牲者名
- 本人への通知内容:無し
#### 例:
GMからの質問"[GM]誰を襲撃しますか？"
人狼の応答"Username"
"""

class GameMaster:
    """
    ゲームの進行を管理するクラス
    """
    def __init__(self, roles: list[Role]):
        """
        コンストラクタ
        """        
        startupMSG = f"""
あなたは人狼ゲームのゲームマスターです。
あなたの仕事は、各エージェント(プレイヤー)の応答を記録し、ゲームの状態を更新することです。
ゲームの状態はあなたのコンテキストによって管理されます。
また、あなたの発言がほかの全エージェントにそのまま伝えられる場合があります。
その際は[公開情報]を付けるため、全エージェントが知っても問題ない情報に絞って発言してください。
また、ゲームのルールは{gameRule}
"""
        self.brain: Brain = GeminiBrain(systemInstruction=startupMSG)
        self.agents: list[Agent] = []
        self.livingAgents: list[Agent] = []
        self.roles: list[Role] = roles
        self.publicGameState: list[str] =[]
        self.privateGameState: list[str] =[]
        self.privateGameLog: list[str] =[]
        self.publicGameLog: list[str] =[]
        self.console = Console()


    def begin(self):
        """
        ゲームの開始
        """
        self.console.print(Panel("[bold cyan]AI人狼ゲームへようこそ！[/bold cyan]", title="ゲーム開始"))

        self.agents = [Agent(f"エージェント{i+1}", GeminiBrain()) for i in range(len(self.roles))]
        self.livingAgents =self.agents

        for i, agent in enumerate(self.agents):
            agent.role = self.roles[i].name
            startupmsg = f"""
あなたはオンライン人狼ゲームの参加者、{agent.name}です。役職は{agent.role}です。
ふるまいは、ゲームルールや、プロンプト: {self.roles[i].prompt}を参考にしてください。
他の参加者は{", ".join([agent.name for agent in self.agents])}です。
ほかのプレイヤーは人間であり、{agent.name}がAIであることは秘匿されています。
そのため人間らしいふるまいを行ってください。
また、これがテキストベースのゲームであることを考慮してください。つまり、{agent.name}の得意な整形された文章は不自然ですので注意してください。
また、回答時には括弧を付けたり、発言""のようにしないで、平文でお願いします。
f"ただいまより人狼ゲームを開始します。"
ゲームのルールは、{gameRule}
"""
            agent.brain = GeminiBrain(startupmsg)

            

        agentRoleMap = {agent.name: agent.role for agent in self.agents}
        agentRoleMapStr = ", ".join([f"{name}: {role}" for name, role in agentRoleMap.items()])
        self.brain.notice("[Notice]各エージェントの役職は"+agentRoleMapStr)

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
        while True:
            self.console.print(Panel(f"[cyan]====== {day}日目 ======[/cyan]", expand=False))

            # --- 夜のターン ---
            notyfy = f"{day}日目 - 夜" + "[bold blue]夜が来ました。各役職は行動してください。[/bold blue]"
            self.noticeBCast(notyfy, self.agents)
            self.console.print(Panel("[bold blue]夜が来ました。各役職は行動してください。[/bold blue]", title=f"{day}日目 - 夜"))
            nestPanel = NestPanel(title=notyfy)
            with Live(nestPanel.parentPanel, console=self.console, refresh_per_second=4, transient=False) as live:
                for agent in self.livingAgents:
                    with self.console.status(f"{agent}が行動中...") as status:
                        thought = agent.talk(f"[ゲームマスター]あなた({agent.name})の役職に基づいた最適な行動を200字以内で推測してください")
                        action = agent.talk("[ゲームマスター]あなた({agent.name})に夜間役職行動がある場合、行動内容を簡潔に述べてください。")
                        actionresult = self.brain.talk(f"夜の行動: {agent}が「{action}」と行動しました。もし、結果がある行動(例：占いの結果)なら、その結果を通知してください。なければNoneを出力。")
                        agent.notice("[Notice]の行動が結果のある行動の場合は結果が入ります。:"+str(actionresult))
                    newChildPanel = Panel(Group(
                        Panel(f"{thought}", title=f"考察"), 
                        Panel(f"{action}",title=f"{agent}の夜の行動"),
                        Panel(f"{actionresult}",title=f"行動の結果"),
                        ), style="bold blue")
                    #self.console.print(Panel(f"思考: {tmp}\n行動: {action}\n結果: {actionresult}", title=f"{agent}", style="bold blue"))
                    nestPanel.append(newChildPanel)


            self.console.print("夜の行動が終了しました。")

            # 夜の行動結果を通知
            with self.console.status("夜の行動結果を集計中...") as status:
                lastNightExplain ="[Notice]"+ self.brain.talk("[公開情報]集計した昨晩の行動による結果を簡潔に教えてください。全ユーザーに通知されるため、秘密情報は出さないでください。")
            self.publicGameState += f"\n{day}日目夜: {lastNightExplain}"
            生存者名一覧 = [agent.name for agent in self.livingAgents]
            self.console.print(Panel(self.publicGameState+ f"\n生存者名一覧:{生存者名一覧}", title="公開情報"))

            self._cheack_reject_agent()



            self.noticeBCast(lastNightExplain, self.agents)

            if self._check_game_end(): break

            # --- 昼のターン ---
            notyfy = "[Notice][bold yellow]昼になりました。議論を開始してください。[/bold yellow]"
            self.console.print(Panel(notyfy, title=f"{day}日目 - 昼"))
            self.conversation(talktheme=notyfy, agents=self.livingAgents, loopcount=2)


            # --- 投票 ---
            notyfy = "[Notyfy][bold red]追放投票の時間です。[/bold red]"
            self.console.print(Panel(notyfy, title=f"{day}日目 - 投票"))
            #voteResult = ""
            votedList = []
                
            nestPanel = NestPanel(title=notyfy)
            with Live(nestPanel.parentPanel, console=self.console, refresh_per_second=0.5, transient=False) as live:
                for agent in self.livingAgents:
                    with self.console.status(f"{agent}が投票先を考察中...") as status:
                        考察 = agent.talk(f"[ゲームマスター]{agent.name}さん、{notyfy}誰を追放するか200文字以内で考察してください。")
                        #self.console.print(f"{agent}の考察: {考察}")
                    with self.console.status(f"{agent}が投票中...") as status:
                        votedList.append(agent.select(
                            text=f"{agent.name}さん、考察の結果、誰に投票しますか？",
                            options=[a.name for a in self.livingAgents]
                        ))
                    newChildPanel = Panel(Group(
                        Panel(f"{考察}", title=f"{agent}の考察"), 
                        Panel(f"{votedList[-1]}",title=f"{agent}の投票")
                        ), style="bold blue")
                    nestPanel.append(newChildPanel)
            
            #最も投票数の多いエージェントを抽出
            voteResult = max(set(votedList), key=votedList.count)
            #self.brain.talk(f"誰が追放されるか教えて。投票結果{voteResult}から、最も投票数の多い人を選んでください。もし同数なら無効投票とします。")
            notyfy =f"[Notyfy]投票結果:\n{voteResult}は追放されました" if voteResult != None else f"投票結果は無効でした。"
            self.noticeBCast(notyfy, self.agents)

            newChildPanel = Panel(notyfy, style="blue")
            nestPanel.append(newChildPanel)
            
            self._cheack_reject_agent()
            if self._check_game_end(): break
            
            day += 1
            
    def end(self):
        """
        ゲームの終了
        """
        gameEndNotice = "[GM][Notice]ゲームが終了しました。"
        self.noticeBCast(gameEndNotice, self.agents)
        self.brain.notice(gameEndNotice)
        winTeam = self.brain.talk("勝利した陣営を教えてください")
        winCause  = self.brain.talk("ゲーム終了の原因を(200文字以内)説明してください。")
        goodPoint  = self.brain.talk("本ゲームの見どころを教えてください。例えば、ゲームチェンジとなった局面などです。")
        self.console.print(Panel(Group(
            Panel(winTeam, title="勝利陣営"), 
            Panel(winCause, title="勝利原因"),
            Panel(goodPoint, title="見どころ")
            ), title="ゲーム終了"))
        
        self.noticeBCast(f"[GM][Notice]勝利陣営:{winTeam}", self.agents)
        self.noticeBCast(f"[GM][Notice]勝利原因:{winCause}", self.agents)
        self.noticeBCast(f"[GM][Notice]見どころ:{goodPoint}", self.agents)
        
        self.console.print("感想戦を開始します。")
        nestPanel = NestPanel(title="感想戦")
        self.conversation(talktheme="感想や見どころ、惜しかったところを200字以内で述べてください。", agents=self.agents, loopcount=2)

    def conversation(self, talktheme: str, agents: list[Agent], loopcount: int) -> str:
        """
        会話のサブルーチン
        """
        #self.console.print(Panel(f"会話テーマ: {talktheme}", title="会話開始", style="bold green"))
        
        conversation_log = f"テーマ: {talktheme}\n"
        nestPanel = NestPanel(title=f"会話テーマ: {talktheme}")
        with Live(nestPanel.parentPanel, console=self.console, refresh_per_second=4, transient=False) as live:
            for i in range(loopcount):
                header = f"--- 議論ターン {i+1} ---"
                self.console.print(header)
                conversation_log += header + "\n"
                for agent in agents:
                    with self.console.status(f"{agent}が発言中...") as status:
                        response =agent.talk(conversation_log)
                    conversation_log += f"{agent.name}: {response}\n"
                    newChildPanel = Panel(f"{agent}:\n {response}", style="bold blue")
                    nestPanel.append(newChildPanel)
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
        txt= """現在、ゲームの終了条件に合致しますか？ルールは
        - 人狼陣営の勝利条件は、市民陣営のと人狼陣営を同数以下にすること。
        - 市民陣営の勝利条件は、人狼陣営を全滅させることです。
        - いずれかの陣営の勝利が確定している場合、'終了'を出力し、そうでないなら'継続'を出力してください。
        """
        with self.console.status("ゲームの終了条件を確認中...") as status:
            endTxt = self.brain.select(txt, ["終了", "継続"])
        return endTxt == "終了"
    
    def _cheack_reject_agent(self):
        agentToReject =  self.brain.select("除外されるエージェントが存在するなら選択して", [agent.name for agent in self.livingAgents])
        self.livingAgents = list(filter(lambda agent: agent.name != agentToReject, self.livingAgents))