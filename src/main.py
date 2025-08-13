from GameMaster import GameMaster
from Role import Role
import random
def main():
    """
    ゲームのメイン実行関数
    """
    roles = [
        Role(name="人狼", prompt="あなたは人狼です。毎晩、市民を一人襲撃してください。"),
        Role(name="占い師", prompt="あなたは占い師です。毎晩、一人のプレイヤーの役職を知ることができます。"),
        Role(name="市民", prompt="あなたは市民です。人狼を見つけ出し、追放してください。"),
        Role(name="市民", prompt="あなたは市民です。人狼を見つけ出し、追放してください。")
    ]
    random.shuffle(roles)
    gm = GameMaster(roles=roles)
    gm.begin()
    gm.gameloop()

if __name__ == "__main__":
    main()
