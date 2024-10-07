import aiohttp
import requests
import random
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl


class TTS:
    def __init__(self) -> None:
        self.getAccessTokenApi()
        self.player = QMediaPlayer()

    def getAccessTokenApi(self):
        url = "https://auth-ai.vip.sankuai.com/oauth/v2/token?grant_type=client_credentials&client_id=cYv/61fSOJPhlMebCH2rTdZKSzVaHiDL2Z/X2n1eGGY=&client_secret=e5c8565682854c0e864ed508cdd91204"
        res = requests.post(url=url)
        print(res)

    def guid():
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

    async def ttsStart(self, text):
        url = "https://speech.meituan.com/tts/v1/stream"
        data = {
            "text": "你好，测试测试",
            "voice_name": 'lm_9f58c_b6cbb',
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
        file_path = "output.mp3"
        async with aiohttp.ClientSession() as session:
            await self.fetch_and_save_pcm(session, url, data, headers, file_path)
            print(f"file saved to {file_path}")

    def play(self):
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile('path/to/your/music.mp3')))
        self.player.mediaStatusChanged.connect(self.onMediaStatusChanged)
        self.player.play()

    def stopTTS(self):
        self.player.stop()
        
    def onMediaStatusChanged(self, status):
        if status == QMediaPlayer.EndOfMedia:
            print('Music playback finished')