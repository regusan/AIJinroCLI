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

class GameMaster:
    """
    ゲームの進行を管理するクラス
    """
    def __init__(self, agents:List[Agent], gmBrain:Brain):
        """
        コンストラクタ
        """        
        self.brain: Brain = gmBrain
        self.agents: list[Agent] = agents
        self.livingAgents: list[Agent] = agents
        self.publicGameState: list[str] =[]
        self.privateGameState: list[str] =[]
        self.privateGameLog: list[str] =[]
        self.publicGameLog: list[str] =[]
        self.console = Console()


    def begin(self):
        """
        ゲームの開始
        """
        self.console.print(Panel("[bold cyan]AI人狼ゲームへようこそ![/bold cyan]", title="ゲーム開始"))

        self.livingAgents =self.agents

        agentRoleMap = {agent.name: agent.role for agent in self.agents}
        agentRoleMapStr = ", ".join([f"{name}: {role}" for name, role in agentRoleMap.items()])
        self.brain.notice("[Notice]各エージェントの役職は"+agentRoleMapStr)

        self.console.print(Rule("各エージェントに役職を割り振りました。"))
        sannka = f"参加者: {len(self.agents)}名"
        self.publicGameState.append(sannka)

        agentInfo = "\n".join([f"{agent.name}: {agent.role}" for agent in self.agents])
        self.privateGameState.append(agentInfo)
        self.console.print(Panel(f"{sannka}\n{agentInfo}", title="参加者", style="bold red"))


    def gameloop(self):
        """
        ゲームのメインループ
        """

        self.console.print(Panel("[bold magenta]ゲームループ開始[/bold magenta]"))
        day = 1
        while True:
            self.console.print(Rule(f"[cyan]====== {day}日目夜 ======[/cyan]"))

            # --- 夜のターン ---
            notyfy = f"{day}日目 - 夜" + "[bold blue]夜が来ました。各役職は行動してください。[/bold blue]"
            self.noticeBCast(notyfy, self.agents)
            nestPanel = NestPanel(title=notyfy)
            with Live(nestPanel.parentPanel,screen=False, console=self.console, refresh_per_second=4, transient=False, vertical_overflow="crop") as live:
                for agent in self.livingAgents:
                    with live.console.status(f"{agent}が行動中...") as _:
                        thought = agent.talk(f"[ゲームマスター]あなた({agent.name})の役職に基づいた最適な行動を200字以内で推測してください")
                        action = agent.talk(f"[ゲームマスター]あなた({agent.name})に夜間役職行動がある場合、行動内容を簡潔に述べてください。")
                        actionresult = self.brain.talk(f"夜の行動: {agent}が「{action}」と行動しました。もし、結果がある行動(例：占いの結果)なら、その結果を通知してください。なければNoneを出力。")
                        agent.notice("[Notice]の行動が結果のある行動の場合は結果が入ります。:"+str(actionresult))
                        newChildPanel = Panel(Group(
                            Panel(f"{thought}", title=f"考察"), 
                            Panel(f"{action}",title=f"夜の行動"),
                            Panel(f"{actionresult}",title=f"行動の結果"),
                            ), style="bold blue", title=str(agent))
                        nestPanel.append(newChildPanel)


            # 夜の行動結果を通知
            with self.console.status("夜の行動結果を集計中...") as status:
                lastNightExplain ="[Notice]"+ self.brain.talk("[公開情報]集計した昨晩の行動による結果を簡潔に教えてください。全ユーザーに通知されるため、秘密情報は出さないでください。")
            actionResult = f"{day}日目夜: {lastNightExplain}"
            self.publicGameState +=f"\n{actionResult}"
            生存者名一覧 = [agent.name for agent in self.livingAgents]
            self.console.print(Panel(actionResult+ f"\n生存者名一覧:{生存者名一覧}", title="昨晩の出来事", style="bold red"))

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
            votedList:list[str] = []
                
            nestPanel = NestPanel(title=notyfy)
            with Live(nestPanel.parentPanel, console=self.console, refresh_per_second=0.5, transient=False, vertical_overflow="crop") as live:
                for agent in self.livingAgents:
                    with self.console.status(f"{agent}が投票先を考察中...") as _:
                        考察 = agent.talk(f"[ゲームマスター]{agent.name}さん、{notyfy}誰を追放するか200文字以内で考察してください。")
                        #self.console.print(f"{agent}の考察: {考察}")
                    with self.console.status(f"{agent}が投票中...") as _:
                        votedList.append(agent.select(
                            text=f"{agent.name}さん、考察の結果、誰に投票しますか？",
                            options=[a.name for a in self.livingAgents]
                        ))
                    newChildPanel = Panel(Group(
                        Panel(f"{考察}", title=f"考察"), 
                        Panel(f"{votedList[-1]}",title=f"投票")
                        ), style="bold blue", title=str(agent))
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
        allTurnConversationLog = f"テーマ: {talktheme}\n"
        nestPanel = NestPanel(title=f"会話テーマ: {talktheme}")
        self.noticeBCast(talktheme, agents)
        with Live(nestPanel.parentPanel, console=self.console, refresh_per_second=4, transient=False, vertical_overflow="crop") as live:
            for i in range(loopcount):
                header = f"--- 議論ターン {i+1} ---"
                self.noticeBCast(header, agents)
                nestPanel.append(Rule(header))
                allTurnConversationLog += header + "\n"
                for agent in agents:
                    with self.console.status(f"{agent}が発言中...") as status:
                        response = agent.talk("[GM]あなたのターンです。議論を開始してください。")
                        self.noticeBCast(f"{agent.name}:\n {response}", agents)
                        allTurnConversationLog += f"{agent.name}: {response}\n"
                        newChildPanel = Panel(f"{agent}:\n {response}", style="bold blue")
                        nestPanel.append(newChildPanel)
        return allTurnConversationLog

    def noticeBCast(self, bcastText:str, agents:list[Agent]):
        """
        全エージェントにブロードキャストメッセージを送信する
        """
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
        self.brain.popLog(2)#記憶する必要はないので忘れる
        return endTxt == "終了"
    
    def _cheack_reject_agent(self):
        agentToReject =  self.brain.select("除外されるエージェントが存在するなら選択して", [agent.name for agent in self.livingAgents])
        self.livingAgents = list(filter(lambda agent: agent.name != agentToReject, self.livingAgents))
        self.brain.popLog(2)#記憶する必要はないので忘れる
        return