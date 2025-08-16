from Agent import Agent
from GeminiBrain import GeminiBrain
from Brain import Brain
from Role import Role
from rich.console import Console
from rich.panel import Panel
from rich.console import Group
from rich.rule import Rule
from rich.live import Live
import random
from typing import List, Tuple, Dict

from NestPanel import NestPanel

class ColorPallet:
    gm = "cyan"
    agent = "blue"
    accent = "bold magenta"
    system = "bold green"
    important = "bold red"
    importantSub = "red"

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
        self.col = ColorPallet()


    def begin(self):
        """
        ゲームの開始
        """
        self.console.print(Panel(f"[{self.col.system}]AI人狼ゲームへようこそ![/{self.col.system}]"))

        self.livingAgents =self.agents

        agentRoleMap = {agent.name: agent.role for agent in self.agents}
        agentRoleMapStr = ", ".join([f"{name}: {role}" for name, role in agentRoleMap.items()])
        self.brain.notice(f"各エージェントの役職は{agentRoleMapStr}")

        self.console.print(Rule(f"[{self.col.system}]各エージェントに役職を割り振りました。[/{self.col.system}]"))
        sannka = f"[{self.col.system}]参加者:[/{self.col.system}] [{self.col.accent}]{len(self.agents)}[/{self.col.accent}]名"
        self.publicGameState.append(sannka)

        agentInfo = "\n".join([f"[{self.col.accent}]{agent.name}[/{self.col.accent}]: {agent.role}" for agent in self.agents])
        self.privateGameState.append(agentInfo)
        self.console.print(Panel(f"{sannka}\n{agentInfo}", title="参加者", style=self.col.importantSub))


    def gameloop(self):
        """
        ゲームのメインループ
        """

        self.console.print(Panel(f"[{self.col.system}]ゲームループ開始[/{self.col.system}]"))
        day = 1
        while True:
            self.console.print(Rule(f"[{self.col.accent}]====== {day}日目夜 ======[/{self.col.accent}]"))

            # --- 夜のターン ---
            notyfy = f"[{self.col.accent}]{day}日目 - 夜[/{self.col.accent}] [{self.col.gm}]夜が来ました。各役職は行動してください。[/{self.col.gm}]"
            notyfy_plain = f"{day}日目 - 夜 夜が来ました。各役職は行動してください。"
            self.noticeBCast(notyfy, self.agents)
            nestPanel = NestPanel(title=notyfy)
            with Live(nestPanel.parentPanel,screen=False, console=self.console, auto_refresh=False, transient=False, vertical_overflow="crop") as live:
                for agent in self.livingAgents:
                    with live.console.status(f"[{self.col.agent}]{agent}[/{self.col.agent}]が行動中...") as _:
                        thought = agent.talk(f"あなた({agent.name})の役職に基づいた最適な行動を200字以内で推測してください")
                        action = agent.talk(f"あなた({agent.name})に夜間役職行動がある場合、行動内容を簡潔に述べてください。")
                        actionresult = self.brain.talk(f"夜の行動: {agent}が「{action}」と行動しました。もし、結果がある行動(例：占いの結果)なら、その結果を通知してください。なければNoneを出力。")
                        agent.notice(f"の行動が結果のある行動の場合は結果が入ります。:{str(actionresult)}")
                        newChildPanel = Panel(Group(
                            Panel(f"{thought}", title=f"[{self.col.system}]考察[/{self.col.system}]"), 
                            Panel(f"{action}",title=f"[{self.col.system}]夜の行動[/{self.col.system}]"),
                            Panel(f"{actionresult}",title=f"[{self.col.system}]行動の結果[/{self.col.system}]"),
                            ), style=self.col.agent, title=str(agent))
                        nestPanel.append(newChildPanel)
                        live.refresh()


            # 夜の行動結果を通知
            with self.console.status(f"[{self.col.system}]夜の行動結果を集計中...[/{self.col.system}]") as status:
                lastNightExplain_plain = self.brain.talk("[公開情報]集計した昨晩の行動による結果を簡潔に教えてください。全ユーザーに通知されるため、秘密情報は出さないでください。")
                lastNightExplain = f"[{self.col.gm}][Notice][/{self.col.gm}]{lastNightExplain_plain}"

            actionResult = f"[{self.col.accent}]{day}日目夜:[/{self.col.accent}] {lastNightExplain}"
            self.publicGameState +=f"\n{actionResult}"
            生存者名一覧 = [f"[{self.col.accent}]{agent.name}[/{self.col.accent}]" for agent in self.livingAgents]
            self.console.print(Panel(actionResult+ f"\n[{self.col.system}]生存者名一覧:[/{self.col.system}]{生存者名一覧}", title="昨晩の出来事", style=self.col.importantSub))

            self._cheack_reject_agent()



            self.noticeBCast(lastNightExplain, self.agents)

            if self._check_game_end(): break

            # --- 昼のターン ---
            notyfy = f"[{self.col.gm}][Notice][/{self.col.gm}] [{self.col.accent}]昼になりました。議論を開始してください。[/{self.col.accent}]"
            self.console.print(Panel(notyfy, title=f"{day}日目 - 昼", style=self.col.accent))
            self.conversation(talktheme=notyfy, agents=self.livingAgents, loopcount=2)


            # --- 投票 ---
            notyfy = f"[{self.col.important}][Notyfy]追放投票の時間です。[/{self.col.important}]"
            notyfy_plain = "追放投票の時間です。"
            self.console.print(Panel(notyfy, title=f"{day}日目 - 投票", style=self.col.accent))
            #voteResult = ""
            votedList:list[str] = []
                
            nestPanel = NestPanel(title=notyfy)
            with Live(nestPanel.parentPanel, console=self.console, auto_refresh=False, transient=False, vertical_overflow="crop") as live:
                option:list[str] = [a.name for a in self.livingAgents]
                option.append("None")
                for agent in self.livingAgents:
                    with self.console.status(f"[{self.col.agent}]{agent}[/{self.col.agent}]が投票先を考察中...") as _:
                        考察 = agent.talk(f"{agent.name}さん、{notyfy_plain}誰を追放するか200文字以内で考察してください。")
                        #self.console.print(f"{agent}の考察: {考察}")
                    with self.console.status(f"[{self.col.agent}]{agent}[/{self.col.agent}]が投票中...") as _:
                        votedList.append(agent.select(
                            text=f"{agent.name}さん、考察の結果、誰に投票しますか？",
                            options=option
                        ))
                    newChildPanel = Panel(Group(
                        Panel(f"{考察}", title=f"[{self.col.system}]考察[/{self.col.system}]"), 
                        Panel(f"[{self.col.accent}]{votedList[-1]}[/{self.col.accent}]",title=f"[{self.col.system}]投票[/{self.col.system}]")
                        ), style=self.col.agent, title=str(agent))
                    nestPanel.append(newChildPanel)
                    live.refresh()
            
            #最も投票数の多いエージェントを抽出
            voteResult = max(set(votedList), key=votedList.count)
            #self.brain.talk(f"誰が追放されるか教えて。投票結果{voteResult}から、最も投票数の多い人を選んでください。もし同数なら無効投票とします。")
            notyfy =f"[{self.col.important}][Notyfy]投票結果:\n[{self.col.accent}]{voteResult}[/{self.col.important}]は追放されました[/{self.col.important}]" if voteResult != None else f"[{self.col.important}]投票結果は無効でした。[/{self.col.important}]"
            self.noticeBCast(notyfy, self.agents)

            newChildPanel = Panel(notyfy, style=self.col.important)
            nestPanel.append(newChildPanel)
            
            self._cheack_reject_agent()
            if self._check_game_end(): break
            
            day += 1
            
    def end(self):
        """
        ゲームの終了
        """
        gameEndNotice = f"[{self.col.gm}][Notice]ゲームが終了しました。[/{self.col.gm}]"
        gameEndNotice_plain = "ゲームが終了しました。"
        self.noticeBCast(gameEndNotice, self.agents)
        self.brain.notice(gameEndNotice_plain)
        winTeam = self.brain.talk("勝利した陣営を教えてください")
        winCause  = self.brain.talk("ゲーム終了の原因を(200文字以内)説明してください。")
        goodPoint  = self.brain.talk("本ゲームの見どころを教えてください。例えば、ゲームチェンジとなった局面などです。")
        self.console.print(Panel(Group(
            Panel(winTeam, title=f"[{self.col.system}]勝利陣営[/{self.col.system}]"), 
            Panel(winCause, title=f"[{self.col.system}]勝利原因[/{self.col.system}]"),
            Panel(goodPoint, title=f"[{self.col.system}]見どころ[/{self.col.system}]")
            ), title="ゲーム終了"))
        
        self.noticeBCast(f"[{self.col.gm}][Notice]勝利陣営:[/{self.col.gm}][{self.col.accent}]{winTeam}[/{self.col.accent}]", self.agents)
        self.noticeBCast(f"[{self.col.gm}][Notice]勝利原因:[/{self.col.gm}]{winCause}", self.agents)
        self.noticeBCast(f"[{self.col.gm}][Notice]見どころ:[/{self.col.gm}]{goodPoint}", self.agents)
        
        self.console.print(f"[{self.col.system}]感想戦を開始します。[/{self.col.system}]")
        nestPanel = NestPanel(title="感想戦")
        self.conversation(talktheme=f"[{self.col.system}]感想や見どころ、惜しかったところを200字以内で述べてください。[/{self.col.system}]", agents=self.agents, loopcount=2)

    def conversation(self, talktheme: str, agents: list[Agent], loopcount: int) -> str:
        """
        会話のサブルーチン
        """
        allTurnConversationLog = f"[{self.col.system}]テーマ:[/{self.col.system}] {talktheme}\n"
        nestPanel = NestPanel(title=f"会話テーマ: {talktheme}")
        self.noticeBCast(talktheme, agents)
        with Live(nestPanel.parentPanel, console=self.console, auto_refresh=False, transient=False, vertical_overflow="crop") as live:
            for i in range(loopcount):
                header = f"--- [{self.col.accent}]議論ターン {i+1}[/{self.col.accent}] ---"
                self.noticeBCast(header, agents)
                nestPanel.append(Rule(header))
                allTurnConversationLog += header + "\n"
                for agent in agents:
                    with self.console.status(f"[{self.col.agent}]{agent}[/{self.col.agent}]が発言中...") as status:
                        response = agent.talk("あなたのターンです。議論を開始してください。")
                        self.noticeBCast(f"[{self.col.agent}]{agent.name}[/{self.col.agent}]:\n {response}", agents)
                        allTurnConversationLog += f"{agent.name}: {response}\n"
                        newChildPanel = Panel(f"[{self.col.agent}]{agent}[/{self.col.agent}]:\n {response}", style=self.col.agent)
                        nestPanel.append(newChildPanel)
                        live.refresh()

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
        txt= '''現在、ゲームの終了条件に合致しますか？ルールは
        - 人狼陣営の勝利条件は、市民陣営のと人狼陣営を同数以下にすること。
        - 市民陣営の勝利条件は、人狼陣営を全滅させることです。
        - いずれかの陣営の勝利が確定している場合、'終了'を出力し、そうでないなら'継続'を出力してください。
        '''
        with self.console.status(f"[{self.col.system}]ゲームの終了条件を確認中...[/{self.col.system}]") as status:
            endTxt = self.brain.select(txt, ["終了", "継続"])
        self.brain.popLog(2)#記憶する必要はないので忘れる
        return endTxt == "終了"
    
    def _cheack_reject_agent(self):
        options:List[str] = [agent.name for agent in self.livingAgents]
        options.append("None")
        agentToReject =  self.brain.select("除外されるエージェントが存在するなら選択して", options)
        self.livingAgents = list(filter(lambda agent: agent.name != agentToReject, self.livingAgents))
        self.brain.popLog(2)#記憶する必要はないので忘れる
        return