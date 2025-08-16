from GameMaster import GameMaster
import GameSettings as gs
from Agent import Agent
from Role import Role
from Brain import Brain
from GeminiBrain import GeminiBrain
import random

def main():
    """
    ゲームのメイン実行関数
    """
    persona = ""

    agents = [
        Agent("太郎", brain=GeminiBrain(), role= gs.roles[gs.人狼], persona=persona),
        Agent("花子", brain=GeminiBrain(), role= gs.roles[gs.占い師], persona=persona),
        Agent("一郎", brain=GeminiBrain(), role= gs.roles[gs.市民], persona=persona),
        Agent("二郎", brain=GeminiBrain(), role= gs.roles[gs.市民], persona=persona),
        Agent("3郎", brain=GeminiBrain(), role= gs.roles[gs.市民], persona=persona),
        Agent("4郎", brain=GeminiBrain(), role= gs.roles[gs.市民], persona=persona),
        ]
        
    allAgentName=", ".join([a.name for a in agents])
    for agent in agents:
        agent.brain.UpdateSystemInstruction(gs.explainYours.format(agent=agent,allAgentName=allAgentName))


    gmBrain = GeminiBrain(systemInstruction=gs.gmSystemInstruction.format(allAgentNames=allAgentName))

    random.shuffle(agents)
    gm = GameMaster(agents=agents, gmBrain=gmBrain)
    gm.begin()
    gm.gameloop()
    gm.end()

if __name__ == "__main__":
    main()
