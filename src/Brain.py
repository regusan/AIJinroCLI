from abc import ABC, abstractmethod

class Brain(ABC):
    """
    AIモデルごとに異なる処理を記述する抽象クラス
    """
    @abstractmethod
    def notice(self, text: str):
        """LLMに通知する。返答はなし。

        Args:
            text (str): 通知内容
        """
        pass

    @abstractmethod
    def talk(self, text: str) -> str:
        """LLMとお話しする

        Args:
            text (str): お話しする内容


        Returns:
            str: 返答
        """
        pass

    @abstractmethod
    def select(self, text: str, options: list[str]) -> str:
        """配列から質問に沿った一つの選択肢を返す(list[str]限定)

        Args:
            text (str): 質問内容
            options (list[str]): 選択肢

        Returns:
            str: 選択した要素
        """
        pass
    
    @abstractmethod
    def popLog(self, popCount:int=1):
        """LLMへの会話ログの末尾を削除する。

        Args:
            popCount (int, optional): いくつ削除するか。デフォルトは1. Defaults to 1.
        """
        pass
    
    @abstractmethod
    def UpdateSystemInstruction(self, systemInstruction: str):
        """システムインストラクションを更新する


        Args:
            systemInstruction (str): システムインストラクションテキスト
        """
        pass