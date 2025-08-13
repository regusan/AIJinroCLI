from abc import ABC, abstractmethod

class Brain(ABC):
    """
    AIモデルごとに異なる処理を記述する抽象クラス
    """
    @abstractmethod
    def notice(self, text: str):
        pass
