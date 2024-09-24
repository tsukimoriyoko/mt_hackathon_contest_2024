import random
import time

from PyQt5.QtCore import (
    QObject,
    QTimer,
    Qt,
    QSize,
    QThread,
    pyqtSignal,
    QMetaObject,
    Q_ARG,
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

from core import action
from core.ability import Ability
from core.conf import settings
from core.ws_client import WebSocketClient


class DesktopPet(QMainWindow):
    def __init__(self, parent=None, tray=False):
        super(DesktopPet, self).__init__(parent)
        self.imgDir = settings.SETUP_DIR / "img"
        self.tray = tray
        self.showOverlay = False
        self.initUI()
        self.pet.startMovie()
        self.initChat()

    def initUI(self):
        self.setWindowIcon(QIcon(str(self.imgDir / settings.ICON)))
        self.desktop = QApplication.desktop()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)  # 背景透明
        point = self.desktop.availableGeometry().bottomRight()
        self.setGeometry(point.x() - 800, point.y() - 1200, 600, 1000)

        self.button1 = QPushButton(self)
        self.button1.setGeometry(0, 700, 64, 64)
        self.button1.setIcon(QIcon(str(self.imgDir / "config.png")))
        self.button1.setIconSize(QSize(64, 64))
        self.button1.setStyleSheet("border-radius: 32;")
        self.button1.clicked.connect(self.onClick1)
        self.button1.hide()
        self.button2 = QPushButton(self)
        self.button2.setGeometry(0, 800, 64, 64)
        self.button2.setIcon(QIcon(str(self.imgDir / "config.png")))
        self.button2.setIconSize(QSize(64, 64))
        self.button2.setStyleSheet("border-radius: 32;")
        self.button2.clicked.connect(self.onClick2)
        self.button2.hide()
        self.button3 = QPushButton(self)
        self.button3.setGeometry(0, 900, 64, 64)
        self.button3.setIcon(QIcon(str(self.imgDir / "config.png")))
        self.button3.setIconSize(QSize(64, 64))
        self.button3.setStyleSheet("border-radius: 32;")
        self.button3.clicked.connect(self.onClick3)
        self.button3.hide()

        self.contentWidget = QWidget(self)
        self.contentWidget.setGeometry(0, 100, 600, 600)

        self.textEdit = QTextEdit(self.contentWidget)
        self.textEdit.setGeometry(0, 550, 480, 64)
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
        self.sendButton.setIcon(QIcon(str(self.imgDir / "config.png")))
        self.sendButton.setIconSize(QSize(64, 64))
        self.sendButton.setGeometry(480 - 64, 550, 64, 64)
        self.sendButton.setStyleSheet(
            "border-radius: 32; background-color: rgb(70,70,70)"
        )
        self.sendButton.clicked.connect(self.sendMessage)

        self.resetButton = QPushButton(self.contentWidget)
        self.resetButton.setIcon(QIcon(str(self.imgDir / "config.png")))
        self.resetButton.setIconSize(QSize(64, 64))
        self.resetButton.setGeometry(480 + 16, 550, 64, 64)
        self.resetButton.setStyleSheet(
            "border-radius: 32; background-color: rgb(70,70,70)"
        )
        self.resetButton.clicked.connect(self.reReply)

        self.replyLoading = QWidget(self.contentWidget)
        self.replyLoadingText = QLabel(self.replyLoading)
        self.replyLoadingText.setGeometry(0, 550 - 64 - 16, 560, 64)
        self.replyLoadingText.setStyleSheet(
            """
                QLabel { 
                    background-color: rgb(70,70,70); 
                    border-radius: 32; 
                    color : white;                  
                    font-family: "Microsoft YaHei";
                    padding-left: 72; 
                    font-size: 28px; 
                }
            """
        )
        self.replyLoadingText.setText("小龙正在努力思考...")
        self.replyLoadingIcon = QLabel(self.replyLoading)
        self.extraInputHeight = 0
        self.replyLoadingIcon.setGeometry(0, 550 - 64 - 16, 64, 64)
        self.replyLoadingIcon.setScaledContents(True)
        loadingPixmap = QPixmap(str(self.imgDir / "config.png"))
        self.replyLoadingIcon.setPixmap(loadingPixmap)
        self.replyLoading.hide()

        self.replyView = QTextEdit(self.contentWidget)
        self.replyViewHeight = 64
        self.replyView.setGeometry(
            0, 550 - 16 - self.replyViewHeight, 560, self.replyViewHeight
        )
        self.replyView.setStyleSheet(
            """
                QTextEdit { 
                    background-color: rgba(0,0,0, 0.6);
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

        self.pet = PetWidget(self)
        self.pet.setGeometry(100, 600, 400, 400)
        self.pet.setPix(str(self.imgDir / settings.INIT_PICTURE))

        self.setCentralWidget(self.contentWidget)

        if self.tray:
            self.trayMenu()  # 系统托盘
        # 全局快捷键
        keyboard.add_hotkey("ctrl+alt+w", self.switchOverlayActive)

    def adjustInputHeight(self):
        # 根据文本内容调整QTextEdit的高度
        document = self.textEdit.document()
        documentSize = document.size()
        newHeight = int(documentSize.height()) + 20  # 适当增加高度以避免滚动条
        if self.textEdit.size().height() != newHeight:
            self.textEdit.setFixedHeight(newHeight)
            self.extraInputHeight = newHeight - 64
            # print("adjustInputHeight", documentSize.height())
            self.textEdit.setGeometry(0, 550 - self.extraInputHeight, 480, 64)
            self.replyView.setGeometry(
                0,
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
        # QTimer.singleShot(2000, self.receiveMessage)

    def reReply(self):
        # TODO
        print("reReply")
        self.replyView.hide()
        self.replyLoading.show()

    def receiveMessage(self, text):
        self.replyView.setText(text)
        self.replyLoading.hide()
        self.replyView.show()

    def adjustOutputHeight(self):
        self.replyView.update()
        docSize = self.replyView.document().size()
        # print("adjustOutputHeight", docSize.height())
        self.replyViewHeight = int(docSize.height() + 20)
        self.replyView.setFixedHeight(self.replyViewHeight)
        self.replyView.setGeometry(
            0,
            550 - 16 - self.replyViewHeight,
            560,
            self.replyViewHeight,
        )

    def initChat(self):
        self.userName = "123"
        self.userId = 1  # TODO
        self.agentId = "ailong"  # TODO
        self.chatClient = WebSocketClient("wss://data.test.meituan.com/channel/chat/1")
        self.chatClient.received.connect(self.onRecvMessage)
        self.chatClient.lost_connection.connect(self.lostConnection)
        print("init chat success, userId: ", self.userId)

    def sendChatMessage(self, text):
        message = f"{{'userId': {self.userId}, 'agentId': '{self.agentId}', 'type': 'text', 'content': '{text}', 'userName': '{self.userName}'}}"
        print('SendMessage', message)
        self.chatClient.sendMessage(message)

    def onRecvMessage(self, status, message, data, traceId):
        self.receiveMessage(data)

    def lostConnection(self):
        self.replyLoading.hide()
        self.textEdit.setText(self.lastSentMsg)

    def trayMenu(self):
        tray = QSystemTrayIcon(self)
        tray.setIcon(QIcon(str(self.imgDir / settings.TRAY_ICON)))
        tray.show()

    def switchOverlayActive(self):
        self.showOverlay = not self.showOverlay
        print("switchOverlayActive", self.showOverlay)

    def mousePressEvent(self, event):
        # if self.playing:
        #     return
        if event.button() == Qt.LeftButton:
            self.pet.walking = False  # 单击 关闭跑步
            self.pet.draging = True
            self.mDragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseReleaseEvent(self, event):
        # 双击鼠标 启动walk, 所以释放的时候要判断是否是双击的情况
        if self.pet.walking is False:
            self.pet.setPix(str(self.imgDir / settings.INIT_PICTURE))
            self.pet.draging = False

    def mouseMoveEvent(self, event):
        # if self.playing or self.walking:
        #     return
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.mDragPosition)
            moveDistance = (self.mDragPosition - event.pos()).x()
            if -1 <= moveDistance < 0:
                self.pet.setPix(str(self.imgDir / settings.MOUSE_TO_RIGHT_1))
            elif -2 <= moveDistance < -1:
                self.pet.setPix(str(self.imgDir / settings.MOUSE_TO_RIGHT_2))
            elif moveDistance < -2:
                self.pet.setPix(str(self.imgDir / settings.MOUSE_TO_RIGHT_3))

            elif 0 < moveDistance <= 1:
                self.pet.setPix(str(self.imgDir / settings.MOUSE_TO_LEFT_1))
            elif 1 < moveDistance <= 2:
                self.pet.setPix(str(self.imgDir / settings.MOUSE_TO_LEFT_2))
            elif 2 < moveDistance:
                self.pet.setPix(str(self.imgDir / settings.MOUSE_TO_LEFT_3))

    def mouseDoubleClickEvent(self, QMouseEvent):
        if self.pet.playing:
            return
        # if Qt.LeftButton == QMouseEvent.button():
        #     self.pet.walking = True
        #     self.walk()

    def closeEvent(self, QCloseEvent):
        #  如何在walk 的时候关闭, 会导致程序坞的图标不消失,所以要先停掉walk
        self.pet.walking = False

    def contextMenuEvent(self, e):
        # if self.walking or self.playing or self.draging:
        #     return
        self.button1.show()
        self.button2.show()
        self.button3.show()
        self.pet.contenting = True
        menu = QMenu(self)
        ability = Ability(self)

        wechat = menu.addAction("猿神，启动")
        wechat.triggered.connect(ability.openBMW)
        wechat.setIcon(QIcon(str(self.imgDir / settings.WECHAT)))

        close = menu.addAction("退出")
        close.triggered.connect(self.close)
        close.setIcon(QIcon(str(self.imgDir / settings.EXIT)))

        menu.exec_(e.globalPos())
        self.pet.contenting = False

    def focusOutEvent(self, event):
        print("focusOutEvent", event)
        self.button1.hide()
        self.button2.hide()
        self.button3.hide()

    def welcomePage(self):
        """欢迎页面"""

    def onClick1(self):
        print("按钮1被点击")

    def onClick2(self):
        print("按钮2被点击")

    def onClick3(self):
        print("按钮3被点击")


class PetWidget(QWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.imgDir = settings.SETUP_DIR / "img"
        self.playing = False
        self.draging = False
        self.walking = False
        self.contenting = False

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        if hasattr(self, "pix"):
            painter.drawPixmap(self.rect(), self.pix)

    def setPix(self, pix):
        if isinstance(pix, QPixmap):
            self.pix = pix
        else:
            self.pix = QPixmap(pix)
        # self.resize(self.pix.size())
        # self.setMask(self.pix.mask())
        self.update()

    def startMovie(self):
        self.allActions = Action().getAllAction()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.action)
        self.timer.start(settings.MOVIE_TIME_INTERVAL * 1000)

    def walk(self):
        walk = settings.WALK
        i = 0
        while self.walking is True:
            self.move(self.pos().x() - 5, self.pos().y())
            if self.pos().x() < -128:
                self.move(
                    self.desktop.availableGeometry().bottomRight().x() - 50,
                    self.pos().y(),
                )
            self.setPix(str(self.imgDir / walk[i]))
            QApplication.processEvents()
            time.sleep(0.5)
            if i == 1:
                i = 0
            else:
                i += 1

    def action(self):
        if self.draging or self.walking or self.contenting:
            return
        self.playing = True
        currentMovie = random.choice(self.allActions)
        # print("action", currentMovie)
        self.actionTimer = ActionThread(self)
        self.actionTimer.update_signal.connect(self.updateAction)
        self.currentMovie = currentMovie
        self.currentI = 0
        self.actionTimer.start()

    def updateAction(self):
        if self.currentI < len(self.currentMovie):
            self.setPix(self.currentMovie[self.currentI])
            self.currentI += 1
            self.actionTimer.start()
        else:
            self.playing = False
            self.setPix(str(self.imgDir / settings.INIT_PICTURE))


class ActionThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, parent: QObject | None = ...) -> None:
        super().__init__(parent)

    def run(self):
        time.sleep(0.5)
        self.update_signal.emit("sig")


class Action(object):
    def __init__(self):
        self.imgDir = settings.SETUP_DIR / "img"
        self.actionList = []
        self.picturesList = []

    def createPicture(self):
        module = action
        for i in dir(module):
            if i.startswith("__"):
                continue
            pictures = getattr(module, i)
            self.picturesList.append(pictures)

    def createQpixmap(self):
        for indexI, i in enumerate(self.picturesList):
            for indexJ, j in enumerate(i):
                self.picturesList[indexI][indexJ] = QPixmap(str(self.imgDir / j))

    def getAllAction(self):
        self.createPicture()
        self.createQpixmap()
        return self.picturesList
