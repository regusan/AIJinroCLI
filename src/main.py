from GameMaster import GameMaster
import GameSettings as gs
from Agent import Agent
from Role import Role
from Brain import Brain
from GeminiBrain import GeminiBrain
from UserBrain import UserBrain
from OllamaBrain import OllamaBrain
import Persona 
import random

def main():
    """
    ゲームのメイン実行関数
    """
    persona = ""

    agents = [
        Agent("一郎", brain=GeminiBrain(), role= gs.roles[gs.市民], persona=Persona.皮肉屋ペルソナ),
        Agent("二郎", brain=GeminiBrain(), role= gs.roles[gs.市民], persona=Persona.調停者ペルソナ),
        Agent("三郎", brain=GeminiBrain(), role= gs.roles[gs.市民], persona=Persona.分析家ペルソナ),
        Agent("四郎", brain=GeminiBrain(), role= gs.roles[gs.市民], persona=Persona.癇癪ペルソナ),
        Agent("じんた", brain=GeminiBrain(), role= gs.roles[gs.人狼], persona=Persona.分析家ペルソナ),
        Agent("じん子", brain=GeminiBrain(), role= gs.roles[gs.人狼], persona=Persona.皮肉屋ペルソナ),
        Agent("うらた", brain=GeminiBrain(), role= gs.roles[gs.占い師], persona=Persona.調停者ペルソナ),
        Agent("れい子", brain=GeminiBrain(), role= gs.roles[gs.占い師], persona=Persona.分析家ペルソナ),
        ]
        
    allAgentName=", ".join([a.name for a in agents])
    for agent in agents:
        agent.brain.UpdateSystemInstruction(gs.explainYours.format(agent=agent,allAgentName=allAgentName) + f"あなたの人格:\n{agent.persona}")


    gmBrain = GeminiBrain(
        #modelVirsion="gemini-2.5-pro",
        systemInstruction=gs.gmSystemInstruction.format(allAgentNames=allAgentName))

    random.shuffle(agents)
    gm = GameMaster(agents=agents, gmBrain=gmBrain)
    gm.begin()
    gm.gameloop()
    gm.end()

if __name__ == "__main__":
    main()
