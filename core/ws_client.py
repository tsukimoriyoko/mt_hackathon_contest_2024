import asyncio
from websocket import create_connection
from websocket._exceptions import WebSocketConnectionClosedException
import re
import threading
from PyQt5.QtCore import QObject, pyqtSignal

class WebSocketClient(QObject):
    received = pyqtSignal(int, str, str, str)
    lost_connection = pyqtSignal()
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.ws = None
        self.is_running = True
        self.on_message_callback = None
        self.connect()

        thread = threading.Thread(target=self._receiveMessages)
        thread.daemon = True
        thread.start()

    def connect(self):
        self.ws = create_connection(self.url)

    def _receiveMessages(self):
        while self.is_running:
            try:
                result = self.ws.recv()
                pattern = r"WebResponse\(status=(\d+), message=(.*), data=(.*), traceId=(.*)\)"
                match = re.match(pattern, result)
                if match:
                    status = match.group(1)
                    message = match.group(2)
                    data = match.group(3)
                    traceId = match.group(4)
                    print(
                        f"Received: status={status}, message={message}, data={data}, traceId={traceId}"
                    )
                    self.received.emit(status, message, data, traceId)
            except WebSocketConnectionClosedException:
                print("WebSocket connection closed. Reconnecting...")
                self.connect()
                self.lost_connection.emit()

    def sendMessage(self, message):
        self.ws.send(message)

    def close(self):
        self.is_running = False
        asyncio.run(self.ws.close())