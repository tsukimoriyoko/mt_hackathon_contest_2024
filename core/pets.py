import random
import time

from PyQt5.QtCore import (
    QObject,
    QTimer,
    Qt,
    QSize,
    QThread,
    pyqtSignal,
)
from PyQt5.QtGui import QPixmap, QIcon, QPainter
from PyQt5.QtWidgets import (
    QWidget,
    QMenu,
    QApplication,
    QSystemTrayIcon,
    QAction,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QLabel,
)
import keyboard
import requests
import re

from core import action
from core.ability import Ability
from core.conf import settings
from core.ws_client import WebSocketClient
from core.sub_windows import SetupGameWidget, ProfileWidget, ResetWidget
from core.tts import TTS


class DesktopPet(QMainWindow):
    def __init__(self, parent=None, tray=False):
        super(DesktopPet, self).__init__(parent)
        self.imgDir = settings.SETUP_DIR / "img"
        # self.tray = tray
        self.tray = True
        self.showOverlay = False
        self.level = 1
        self.initUI()
        self.initChat()
        self.mDragPosition = None
        # self.tts = TTS()

    def initUI(self):
        self.setWindowIcon(QIcon(str(self.imgDir / settings.ICON)))
        self.desktop = QApplication.desktop()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)  # 背景透明
        point = self.desktop.availableGeometry().bottomRight()
        self.setGeometry(point.x() - 800 - 1600, point.y() - 1200, 600 + 1600, 1000)

        self.chatBtn = QPushButton(self)
        self.chatBtn.setGeometry(90 + 1600, 790, 72, 72)
        self.chatBtn.setIcon(QIcon(str(self.imgDir / "chat.png")))
        self.chatBtn.setIconSize(QSize(72, 72))
        self.chatBtn.setStyleSheet("border-radius: 32;")
        self.chatBtn.clicked.connect(self.onClickChat)
        self.chatBtn.hide()
        self.resetBtn = QPushButton(self)
        self.resetBtn.setGeometry(90 + 16 + 1600, 870, 56, 56)
        self.resetBtn.setIcon(QIcon(str(self.imgDir / "reset.png")))
        self.resetBtn.setIconSize(QSize(56, 56))
        self.resetBtn.setStyleSheet("border-radius: 32;")
        self.resetBtn.clicked.connect(self.onClickReset)
        self.resetBtn.hide()
        self.palyBtn = QPushButton(self)
        self.palyBtn.setGeometry(410 + 1600, 790, 72, 72)
        self.palyBtn.setIcon(QIcon(str(self.imgDir / "play.png")))
        self.palyBtn.setIconSize(QSize(72, 72))
        self.palyBtn.setStyleSheet("border-radius: 32;")
        self.palyBtn.clicked.connect(self.onClickPlay)
        self.palyBtn.hide()
        self.profileBtn = QPushButton(self)
        self.profileBtn.setGeometry(410 + 1600, 870, 56, 56)
        self.profileBtn.setIcon(QIcon(str(self.imgDir / "heart.png")))
        self.profileBtn.setIconSize(QSize(56, 56))
        self.profileBtn.setStyleSheet("border-radius: 32;")
        self.profileBtn.clicked.connect(self.onClickProfile)
        self.profileBtn.hide()

        self.contentWidget = QWidget(self)
        self.contentWidget.setGeometry(0 + 1600, 100, 600, 600)

        self.textEdit = QTextEdit(self.contentWidget)
        self.textEdit.setGeometry(0 + 1600, 550, 480, 64)
        self.textEdit.setPlaceholderText("有什么问题尽管问我")
        self.textEdit.setStyleSheet(
            """
                QTextEdit {
                    background-color: rgb(70,70,70);
                    color: #FFF;
                    font-family: "Microsoft YaHei";
                    font-size: 28px;
                    border-radius: 32;
                    padding-left: 36;
                    padding-top: 8;
                    line-height: 36;
                    text-align: center;
                }
                QTextEdit[placeholder-text="有什么问题尽管问我"] {
                    color: #B2B2B2;
                }
            """
        )
        self.textEdit.setAlignment(Qt.AlignVCenter)
        self.textEdit.textChanged.connect(self.adjustInputHeight)

        self.sendButton = QPushButton(self.contentWidget)
        self.sendButton.setIcon(QIcon(str(self.imgDir / "send.png")))
        self.sendButton.setIconSize(QSize(64, 64))
        self.sendButton.setGeometry(480 - 64 + 1600, 550, 64, 64)
        self.sendButton.setStyleSheet(
            "border-radius: 32; background-color: rgb(70,70,70)"
        )
        self.sendButton.clicked.connect(self.sendMessage)

        self.resetButton = QPushButton(self.contentWidget)
        self.resetButton.setIcon(QIcon(str(self.imgDir / "regenerate.png")))
        self.resetButton.setIconSize(QSize(64, 64))
        self.resetButton.setGeometry(480 + 16 + 1600, 550, 64, 64)
        self.resetButton.setStyleSheet(
            "border-radius: 32; background-color: rgb(70,70,70)"
        )
        self.resetButton.clicked.connect(self.reReply)

        self.replyLoading = QWidget(self.contentWidget)
        self.replyLoadingText = QLabel(self.replyLoading)
        self.replyLoadingText.setGeometry(0 + 1600, 550 - 64 - 16, 560, 64)
        self.replyLoadingText.setStyleSheet(
            """
                QLabel { 
                    background-color: rgb(70,70,70); 
                    border-radius: 32; 
                    color : white;                  
                    font-family: "Microsoft YaHei";
                    padding-left: 60; 
                    font-size: 28px; 
                }
            """
        )
        self.replyLoadingText.setText("小龙正在努力思考...")
        self.replyLoadingIcon = QLabel(self.replyLoading)
        self.extraInputHeight = 0
        self.replyLoadingIcon.setGeometry(28 + 1600, 566 - 64 - 16, 24, 32)
        self.replyLoadingIcon.setScaledContents(True)
        loadingPixmap = QPixmap(str(self.imgDir / "loading.png"))
        self.replyLoadingIcon.setPixmap(loadingPixmap)
        self.replyLoading.hide()

        self.replyView = QTextEdit(self.contentWidget)
        self.replyViewHeight = 64
        self.replyView.setGeometry(
            0 + 1600, 550 - 16 - self.replyViewHeight, 560, self.replyViewHeight
        )
        self.replyView.setStyleSheet(
            """
                QTextEdit { 
                    background-color: rgba(0,0,0,0.6);
                    border-radius: 32;
                    color : white;
                    font-family: "Microsoft YaHei";
                    padding-top: 8;
                    padding-left: 24;
                    font-size: 28px;
                    line-height: 36;
                }
            """
        )
        self.replyView.setEnabled(False)
        self.replyView.setAlignment(Qt.AlignVCenter)
        self.replyView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.replyView.textChanged.connect(self.adjustOutputHeight)
        self.replyView.hide()

        self.pet = PetWidget(self, self.level)
        self.pet.setGeometry(100 + 1600, 600, 400, 400)
        self.pet.welcome()

        self.setCentralWidget(self.contentWidget)

        if self.tray:
            self.trayMenu()  # 系统托盘
        # 全局快捷键
        keyboard.add_hotkey("alt+w", self.switchOverlayActive)

    def adjustInputHeight(self):
        # 根据文本内容调整QTextEdit的高度
        document = self.textEdit.document()
        documentSize = document.size()
        newHeight = int(documentSize.height()) + 20  # 适当增加高度以避免滚动条
        if self.textEdit.size().height() != newHeight:
            self.textEdit.setFixedHeight(newHeight)
            self.extraInputHeight = newHeight - 64
            # print("adjustInputHeight", documentSize.height())
            self.textEdit.setGeometry(0 + 1600, 550 - self.extraInputHeight, 480, 64)
            self.replyView.setGeometry(
                0 + 1600,
                550 - 16 - self.replyViewHeight - self.extraInputHeight,
                560,
                self.replyViewHeight,
            )

    def sendMessage(self):
        text = self.textEdit.toPlainText()
        print("sendMessage", text, text.__len__())
        if text.__len__() == 0:
            return
        self.sendChatMessage(text)  # TODO 发送失败
        self.lastSentMsg = text
        self.textEdit.setText("")
        self.replyView.hide()
        self.replyLoading.show()

    def reReply(self):
        # TODO
        print("reReply")
        self.replyView.hide()
        self.replyLoading.show()

    def receiveMessage(self, text):
        self.replyView.setText(text)
        self.replyLoading.hide()
        self.replyView.show()
        self.pet.speakAction()

    def adjustOutputHeight(self):
        self.replyView.update()
        docSize = self.replyView.document().size()
        # print("adjustOutputHeight", docSize.height())
        self.replyViewHeight = int(docSize.height() + 20)
        self.replyView.setFixedHeight(self.replyViewHeight)
        self.replyView.setGeometry(
            0 + 1600,
            550 - 16 - self.replyViewHeight,
            560,
            self.replyViewHeight,
        )

    def initChat(self):
        self.lastSentMsg = ""
        self.userName = "123"
        self.userId = "ailong1"
        self.agentId = "ailong"  # TODO
        self.chatClient = WebSocketClient(
            f"wss://data.test.meituan.com/channel/chat/{self.userId}"
        )
        self.chatClient.received.connect(self.onRecvMessage)
        self.chatClient.lost_connection.connect(self.lostConnection)
        print("init chat success, userId: ", self.userId)

    def sendChatMessage(self, text):
        message = f"{{'userId': '{self.userId}', 'agentId': '{self.agentId}', 'type': 'text', 'content': '{text}', 'userName': '{self.userName}'}}"
        print("SendMessage", message)
        self.chatClient.sendMessage(message)

    def remove_brackets(self, text):
        result = re.sub(r'（.*?）', '', text)
        return result
    def onRecvMessage(self, status, message, data, needTransform, traceId):
        self.receiveMessage(data)
        textToTTS = self.remove_brackets(data)
        print('textToTTS', textToTTS)
        # TODO TTS
        if needTransform == "true":
            self.pet.upgrade()

    def lostConnection(self):
        self.replyLoading.hide()
        self.textEdit.setText(self.lastSentMsg)

    def trayMenu(self):
        tray = QSystemTrayIcon(self)
        tray.setIcon(QIcon(str(self.imgDir / settings.TRAY_ICON)))
        menu = QMenu()
        close = menu.addAction("退出")
        close.triggered.connect(self.close)
        close.setIcon(QIcon(str(self.imgDir / settings.EXIT)))
        tray.setContextMenu(menu)
        tray.show()

    def switchOverlayActive(self):
        if not self.showOverlay:
            print("")
        else:
            print("")
        self.showOverlay = not self.showOverlay
        print("switchOverlayActive", self.showOverlay)
        # TODO 语音输入
        self.activateWindow()
        self.textEdit.setFocus()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mDragPosition = event.globalPos() - self.pos()
            if self.mDragPosition.y() > 850:
                self.pet.touchBodyAction()
                print("touch body")
            else:
                self.pet.touchHeadAction()
                print("touch head")
            event.accept()

    def mouseReleaseEvent(self, event):
        if self.pet.draging:
            self.pet.defaultAction()
        self.pet.draging = False

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self.mDragPosition == None:
                return
            if not self.pet.draging:
                self.pet.draging = True
                self.pet.moveAction()
            self.move(event.globalPos() - self.mDragPosition)
            # moveDistance = (self.mDragPosition - event.pos()).x()
            # if -1 <= moveDistance < 0:
            #     self.pet.setPix(str(self.imgDir / settings.MOUSE_TO_RIGHT_1))
            # elif -2 <= moveDistance < -1:
            #     self.pet.setPix(str(self.imgDir / settings.MOUSE_TO_RIGHT_2))
            # elif moveDistance < -2:
            #     self.pet.setPix(str(self.imgDir / settings.MOUSE_TO_RIGHT_3))

            # elif 0 < moveDistance <= 1:
            #     self.pet.setPix(str(self.imgDir / settings.MOUSE_TO_LEFT_1))
            # elif 1 < moveDistance <= 2:
            #     self.pet.setPix(str(self.imgDir / settings.MOUSE_TO_LEFT_2))
            # elif 2 < moveDistance:
            #     self.pet.setPix(str(self.imgDir / settings.MOUSE_TO_LEFT_3))

    # def mouseDoubleClickEvent(self, QMouseEvent):
    #     if self.pet.playing:
    #         return
    #     # if Qt.LeftButton == QMouseEvent.button():
    #     #     self.pet.walking = True
    #     #     self.walk()

    def contextMenuEvent(self, e):
        self.chatBtn.show()
        self.resetBtn.show()
        self.palyBtn.show()
        self.profileBtn.show()
        self.chatBtn.raise_()
        self.resetBtn.raise_()
        self.palyBtn.raise_()
        self.profileBtn.raise_()

        # self.pet.contenting = True
        # menu = QMenu(self)
        # ability = Ability(self)

        # close = menu.addAction("退出")
        # close.triggered.connect(self.close)
        # close.setIcon(QIcon(str(self.imgDir / settings.EXIT)))

        # menu.exec_(e.globalPos())
        self.pet.contenting = False

    def focusOutEvent(self, event):
        print("focusOutEvent", event)
        self.chatBtn.hide()
        self.resetBtn.hide()
        self.palyBtn.hide()
        self.profileBtn.hide()

    def welcomePage(self):
        """欢迎页面"""

    def hideBtns(self):
        self.chatBtn.hide()
        self.resetBtn.hide()
        self.palyBtn.hide()
        self.profileBtn.hide()

    def onClickChat(self):
        print("onClickChat")
        self.contentWidget.show()

    def onClickReset(self):
        print("onClickReset")
        self.resetWidget = ResetWidget(
            parent=self, flags=Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.resetWidget.show()
        self.resetWidget.confirm_reset.connect(self.resetChat)
        self.hideBtns()
        self.contentWidget.hide()

    def resetChat(self):
        url = "https://data.test.meituan.com/pc/v1/conversation/reset"
        headers = {"Content-Type": "application/json"}
        data = {"userId": self.userId, "agentId": self.agentId}
        response = requests.post(url, json=data, headers=headers)
        print(response)
        self.level = 1
        self.pet.level = 1
        self.pet.defaultAction()
        self.textEdit.setText("")
        self.replyView.setText("")

    def onClickPlay(self):
        print("onClickPlay")
        self.contentWidget.hide()
        self.gameWidget = SetupGameWidget(
            parent=self, flags=Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.gameWidget.lower()
        self.gameWidget.show()
        self.hideBtns()
        self.contentWidget.hide()

    def onClickProfile(self):
        print("onClickProfile")
        self.profileWidget = ProfileWidget(
            parent=self, flags=Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.profileWidget.lower()
        self.profileWidget.show()
        self.hideBtns()
        self.contentWidget.hide()


class PetWidget(QWidget):
    def __init__(self, parent: QWidget | None, level) -> None:
        super().__init__(parent)
        self.level = level
        levelStr = f"level{self.level}"
        self.imgDir = settings.SETUP_DIR / "img"
        self.actionObj = Action()
        self.allActions = self.actionObj.getAllAction(levelStr)
        self.actionDict = self.actionObj.actions
        self.timer = QTimer(self)
        self.isMoving = False
        self.speakTimer = 0
        self.draging = False

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        if hasattr(self, "pix"):
            painter.drawPixmap(self.rect(), self.pix)

    def setPix(self, pix):
        if isinstance(pix, QPixmap):
            self.pix = pix
        else:
            self.pix = QPixmap(pix)
        self.update()

    def welcome(self):
        # 目前只有一阶段有启动动画
        if self.level == 1:
            self.doAction("start1")
        else:
            self.setPix(str(self.imgDir / settings.INIT_PICTURE))

    def upgrade(self):
        self.doAction(f"upgrade{self.level}")
        self.level += 1

    def defaultAction(self):
        if self.level == 1:
            self.doAction("default1")
        else:
            self.setPix(str(self.imgDir / f"level{self.level}" / "init.png"))

    def speakAction(self):
        self.doAction(f"speak{self.level}")

    def listenAction(self):
        if self.level == 1:
            self.doAction("listen1")

    def touchHeadAction(self):
        if self.level == 1:
            self.doAction("head1")

    def touchBodyAction(self):
        if self.level == 1:
            self.doAction("body1")

    def moveAction(self):
        if self.level == 1:
            self.doAction("move1")

    def doAction(self, state):
        print(state)
        self.state = state
        i = self.actionDict[state]
        movie = self.allActions[i]
        self.actionTimer = ActionThread(self)
        self.actionTimer.update_signal.connect(self.updateAction)
        self.currentMovie = movie
        self.currentI = 0
        self.actionTimer.start()

    def updateAction(self):
        if self.currentI < len(self.currentMovie):
            self.setPix(self.currentMovie[self.currentI])
            self.currentI += 1
            self.actionTimer.start()
        else:
            if self.state in ["start1", "upgrade1", "upgrade2", "body1", "head1"]:
                # 启动、升级、触摸动画结束后切默认状态
                self.defaultAction()
            elif self.state in [
                "default1",
                "move1",
                "listen1",
            ]:
                # 其他动画结束后循环播放
                self.currentI = 0
                self.actionTimer.start()
            elif self.state in [
                "speak1",
                "speak2",
                "speak3",
            ]:
                if self.speakTimer > 1:
                    return
                self.speakTimer += 1
                self.currentI = 0
                self.actionTimer.start()


class ActionThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, parent: QObject | None = ...) -> None:
        super().__init__(parent)

    def run(self):
        time.sleep(0.2)
        self.update_signal.emit("sig")


class Action(object):
    def __init__(self):
        self.actions = {}
        self.picturesList = []

    def createPicture(self):
        module = action
        cnt = 0
        for i in dir(module):
            if i.startswith("__"):
                continue
            pictures = getattr(module, i)
            self.actions[i] = cnt
            cnt += 1
            self.picturesList.append(pictures)
        print(self.actions)

    def createQpixmap(self):
        for indexI, i in enumerate(self.picturesList):
            for indexJ, j in enumerate(i):
                self.picturesList[indexI][indexJ] = QPixmap(str(self.imgDir / j))

    def getAllAction(self, level):
        self.level = level
        self.imgDir = settings.SETUP_DIR / "img"
        self.createPicture()
        self.createQpixmap()
        return self.picturesList
