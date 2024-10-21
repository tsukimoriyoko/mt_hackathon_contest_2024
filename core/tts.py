import aiohttp
import requests
import random
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QObject, pyqtSignal, QUrl


class TTS(QObject):
    play_finish = pyqtSignal()
    cnt = 0
    open = True
    def __init__(self) -> None:
        super().__init__()
        # self.getAccessTokenApi()
        self.player = QMediaPlayer()
        self.player.mediaStatusChanged.connect(self.onMediaStatusChanged)
        self.accessToken = "v1.2bc328ab556a4dcf83d24e4076a7c0c9.86400000.1729316876610-1772448958334500937"

    def getAccessTokenApi(self):
        url = "https://auth-ai.vip.sankuai.com/oauth/v2/token?grant_type=client_credentials&client_id=cYv/61fSOJPhlMebCH2rTdZKSzVaHiDL2Z/X2n1eGGY=&client_secret=e5c8565682854c0e864ed508cdd91204"
        res = requests.post(url=url)
        print(res)

    def guid(self):
        return "".join(
            [
                random.choice("0123456789abcdef") if c == "x" else random.choice("89ab")
                for c in "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
            ]
        )

    async def fetch_and_save_pcm(self, session, url, data, headers, file_path):
        async with session.post(url, data=data, headers=headers) as response:
            content = await response.read()
            with open(file_path, "wb") as f:
                f.write(content)

    def ttsStart(self, text):
        if not self.open:
            return
        self.stopTTS()
        url = "https://speech.meituan.com/tts/v1/stream"
        data = {
            "text": text,
            "voice_name": 'meifanxi',
            "speed": 50,
            "volume": 50,
            "sample_rate": 24000,
            "audio_format": "mp3",
            "enable_extra_volume": 0,
        }
        headers = {
            "Cache-Control": "no-cache",
            "SessionId": self.guid(),
            "Token": self.accessToken,
        }
        self.cnt += 1
        file_path = f"D:\\output_{self.cnt}.mp3"
        response = requests.post(url=url, headers=headers, data=data)
        print(response)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("File saved successfully")
            self.play()
        else:
            print("Request failed with status code:", response.status_code)

    def play(self):
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(f"D:\\output_{self.cnt}.mp3")))
        self.player.play()

    def stopTTS(self):
        self.player.stop()
        
    def onMediaStatusChanged(self, status):
        if status == QMediaPlayer.EndOfMedia:
            print('Music playback finished')
            self.play_finish.emit()