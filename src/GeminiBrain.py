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
    
    models = ["gemini-2.5-flash-lite","gemini-1.5-flash-8b","gemini-2.5-pro","gemini-2.5-flash","gemini-2.5-flash-lite"]
    def __init__(self, systemInstruction = "", modelVirsion = "gemini-1.5-flash-8b", thinking_budget=-1):
        """
        コンストラクタ
        APIキーの取得とモデルの初期化を行う
        """
        self.console = Console()
        self.modelVirsion = modelVirsion
        self.thinking_budget = thinking_budget

        self.talkLog = []
        
        
        # GEMINI_API_KEYが設定されていない場合はエラーを送出
        if "GEMINI_API_KEY" not in os.environ:
            raise ValueError("GEMINI_API_KEY is not set in environment variables.")
        
        #genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        #self.model = genai.GenerativeModel(model, config=types.GenerateContentConfig(thinking_config=z.ThinkingConfig(thinking_budget=0)))
        self.model = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.config = types.GenerateContentConfig(system_instruction=systemInstruction) 
        self.chat = self.model.chats.create(model=self.modelVirsion, config=self.config)
    
    def UpdateSystemInstruction(self, systemInstruction: str):
        self.config.system_instruction = systemInstruction
        
    def talk(self, text: str) -> str:
        """
        会話を行い、コンテキストを更新する
        """
        self.talkLog.append(self._make_content("user", text))
        while True:
            try:#TODO:なんかError500が頻発するから力わざ
                result = self.model.models.generate_content(model=self.modelVirsion, contents=self.talkLog, config=self.config)
                break
            except:
                print("API Runtime Error!!")
                time.sleep(1)

        self.talkLog.append(self._make_content("model", result.text))
        return result.text
        

    def notice(self, text: str):
        """
        通知を受け取り、コンテキストに追加する
        """
        self.talkLog.append(self._make_content("user", f"\n[Notice]: {text}"))
        
        
    def select(self, text: str, options: list[str]) -> str:
        """
        選択肢から一つを選び、コンテキストを更新する
        """
        self.talkLog.append(self._make_content("user", text))
        response = self.model.models.generate_content(
            model=self.modelVirsion,
            contents=self.talkLog,
            config={
                'response_mime_type': 'text/x.enum',
                'response_schema': {
                    "type": "STRING",
                    "enum": options,
                },
            }
        )
        selected_option = response.text.strip()
        self.talkLog.append(self._make_content("model", selected_option))
        
        if selected_option not in options:
            selected_option = None
        return selected_option
    def popLog(self,popCount:int=1):
        for _ in range(popCount):
            if self.talkLog:
                self.talkLog.pop()
                


    @staticmethod
    def _make_content(role: str, text: str):
        return {"role": role, "parts": [{"text": text}]}
        
        

if __name__ == "__main__":
    # 実行例
    # このスクリプトを実行する前に、環境変数にGEMINI_API_KEYを設定してください
    # export GEMINI_API_KEY="YOUR_API_KEY"

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
    history = brain.chat.get_history()
    for message in history:
        print(message)
    print(brain.talkLog)