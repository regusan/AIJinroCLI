from Brain import Brain
from rich.console import Console
import os
from google import genai
import time
from google.genai import types

class GeminiBrain(Brain):
    """
    GeminiBrainのGemini実装
    """
    def __init__(self, modelVirsion = "gemini-2.5-flash-lite"):
        """
        コンストラクタ
        APIキーの取得とモデルの初期化を行う
        """
        self.console = Console()
        self.context: str = ""
        self.modelVersion = modelVirsion
        
        # GEMINI_API_KEYが設定されていない場合はエラーを送出
        if "GEMINI_API_KEY" not in os.environ:
            raise ValueError("GEMINI_API_KEY is not set in environment variables.")
        
        #genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        #self.model = genai.GenerativeModel(model, config=types.GenerateContentConfig(thinking_config=z.ThinkingConfig(thinking_budget=0)))
        self.model = genai.Client()
    def talk(self, text: str) -> str:
        """
        会話を行い、コンテキストを更新する
        """
        self.context += f"\n[User]: {text}"
        response = self.model.models.generate_content(
            model=self.modelVersion,
            contents=self.context,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )
        self.context += f"\n[AI]: {response.text}"
        return response.text

    def notice(self, text: str):
        """
        通知を受け取り、コンテキストに追加する
        """
        #self.console.print(f"[dim]通知({id(self)}): {text}[/dim]")
        self.context += f"\n[Notice]: {text}"

if __name__ == "__main__":
    # 実行例
    # このスクリプトを実行する前に、環境変数にGEMINI_API_KEYを設定してください
    # export GEMINI_API_KEY="YOUR_API_KEY"
    try:
        brain = GeminiBrain()
        brain.notice("[ゲームマスター]あなたは人狼ゲームの参加者の'Agent1'です。あなたの役職は人狼です。")
        brain.notice("[ゲームマスター]4人の参加者(Agent1,2,3,4)のうち、この中に人狼は1人います。")
        brain.notice("[ゲームマスター]1日目の夜になりました。")
        start = time.time()
        response = brain.talk("[ゲームマスター]今夜のターゲットを教えてください。")
        elapsed= time.time()-start
        print(f"AIの応答 {elapsed:.2f}s: {response}")
        start = time.time()
        response2 = brain.talk("考察を教えてください")
        elapsed= time.time()-start
        print(f"AIの応答 {elapsed:.2f}s: {response2}")
    except ValueError as e:
        print(f"エラー: {e}")
