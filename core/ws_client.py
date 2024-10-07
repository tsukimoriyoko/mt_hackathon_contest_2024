import asyncio
from websocket import create_connection
from websocket._exceptions import WebSocketConnectionClosedException, WebSocketBadStatusException
import re
import threading
import time
import schedule
from PyQt5.QtCore import QObject, pyqtSignal, QThread

class WebSocketClient(QObject):
    received = pyqtSignal(int, str, str, str, str)
    lost_connection = pyqtSignal()
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.ws = None
        self.is_running = True
        self.on_message_callback = None
        self.connect()

        self.thread = threading.Thread(target=self._receiveMessages)
        self.thread.daemon = True
        self.thread.start()

        schedule.every(10).seconds.do(self.sendHeartBeat)
        self.heartThread = Thread()
        self.heartThread.start()

    def connect(self):
        try:
            self.ws = create_connection(self.url)
        except WebSocketBadStatusException:
            print("WebSocket create connection failed. Reconnecting...")
            time.sleep(1)
            self.connect()

    def _receiveMessages(self):
        while self.is_running:
            try:
                result = self.ws.recv()
                print(result)
                pattern = r"WebResponse\(status=(\d+), message=(.*), data=AiLongChatResponse\(reply=(.*), stage=(.*), needTransform=(.*)\), traceId=(.*)\)"
                match = re.match(pattern, result)
                if match:
                    status = match.group(1)
                    message = match.group(2)
                    data = match.group(3)
                    stage = match.group(4)
                    needTransform = match.group(5)
                    traceId = match.group(6)
                    print(
                        f"Received: status={status}, message={message}, reply={data}, stage={stage}, needTransform={needTransform}, traceId={traceId}"
                    )
                    self.received.emit(status, message, data, needTransform, traceId)
            except WebSocketConnectionClosedException:
                print("WebSocket connection closed. Reconnecting...")
                self.connect()
                self.lost_connection.emit()

    def sendMessage(self, message):
        self.ws.send(message)
    
    def sendHeartBeat(self):
        print('send heartbeat')
        message = f"{{'userId': 'ailong1', 'agentId': 'ailong', 'type': 'heartbeat', 'content': '1', 'userName': '123'}}"
        self.ws.send(message)

    def close(self):
        self.is_running = False
        asyncio.run(self.ws.close())

class Thread(QThread):
    def __init__(self):
        super(Thread, self).__init__()

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)