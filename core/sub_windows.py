from PyQt5.QtCore import (
    Qt,
    QSize,
    pyqtSignal,
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (
    QWidget,
    QFrame,
    QPushButton,
    QLabel,
    QTextEdit
)
from core.ability import Ability
from core.conf import settings

class SetupGameWidget(QWidget):
    def __init__(self, parent: QWidget | None = ..., flags: Qt.WindowFlags | Qt.WindowType = ...) -> None:
        super().__init__(parent, flags)
        self.imgDir = settings.SETUP_DIR / "img"
        self.setGeometry(180, 120, 1656, 810)
        self.bg = QFrame(self)
        self.bg.setGeometry(0, 0, 1656, 810)
        self.bg.setStyleSheet("background-color: white; border-radius: 16px")
        self.title = QLabel(self)
        self.title.setGeometry(60, 60, 76, 37)
        self.title.setPixmap(QPixmap(str(self.imgDir / "game_title.png")))
        self.closeBtn = QPushButton(self)
        self.closeBtn.setGeometry(1570, 66, 26, 26)
        self.closeBtn.setStyleSheet("background-color: transparent;")
        self.closeBtn.setIcon(QIcon(str(self.imgDir / "close_b.png")))
        self.closeBtn.clicked.connect(self.close)

        self.ability = Ability()
        self.g1 = QPushButton(self)
        self.g1.setGeometry(60, 150, 360, 564)
        self.g1.setIcon(QIcon(str(self.imgDir / "game_bmw.png")))
        self.g1.setIconSize(QSize(360, 564))
        self.g1.clicked.connect(self.startG1)
        self.g2 = QLabel(self)
        self.g2.setGeometry(452, 150, 360, 564)
        self.g2.setPixmap(QPixmap(str(self.imgDir / "game_gs.png")))
        self.g3 = QLabel(self)
        self.g3.setGeometry(844, 150, 360, 564)
        self.g3.setPixmap(QPixmap(str(self.imgDir / "game_ac.png")))
        self.g4 = QLabel(self)
        self.g4.setGeometry(1236, 150, 360, 564)
        self.g4.setPixmap(QPixmap(str(self.imgDir / "game_ssm.png")))
    def startG1(self):
        self.ability.openBMW()
        self.close()

class ProfileWidget(QWidget):
    curCharacter = 1
    selectedCharacter = 1
    maxLevel = 1
    intimacy = 1
    change_signal = pyqtSignal(int)
    initEnd = False
    def __init__(self, curLevel, maxLevel, intimacy, parent: QWidget | None = ..., flags: Qt.WindowFlags | Qt.WindowType = ...) -> None:
        super().__init__(parent, flags)
        self.curCharacter = curLevel
        self.selectedCharacter = curLevel
        self.maxLevel = maxLevel
        self.intimacy = intimacy
        self.imgDir = settings.SETUP_DIR / "img"
        self.setGeometry(-250 + 1600, 170, 500, 766)
        self.bg = QFrame(self)
        self.bg.setGeometry(0, 0, 500, 766)
        self.bg.setStyleSheet("background-color: white; border-radius: 16px")
        self.profileImg = QPixmap(str(self.imgDir / f"profile_{self.curCharacter}.png"))
        self.profileImg.scaled(500, 654)
        self.profile = QLabel(self)
        self.profile.setPixmap(self.profileImg)
        self.profile.setGeometry(0, 0, 500, 654)
        self.profile.setScaledContents(True)
        self.selectBtn = QPushButton(self)
        self.selectBtn.setGeometry(172, 556, 158, 52)
        self.selectBtn.setIcon(QIcon(str(self.imgDir / "change_ch.png")))
        self.selectBtn.setIconSize(QSize(158, 52))
        self.selectBtn.setStyleSheet("background-color: transparent;")
        self.selectBtn.clicked.connect(self.confirm)
        self.leftBtn = QPushButton(self)
        self.leftBtn.setGeometry(24, 236, 20, 36)
        self.leftBtn.setStyleSheet("background-color: transparent;")
        self.leftBtn.setIcon(QIcon(str(self.imgDir / "left.png")))
        self.leftBtn.setIconSize(QSize(20, 36))
        self.leftBtn.clicked.connect(self.left)
        self.rightBtn = QPushButton(self)
        self.rightBtn.setGeometry(460, 236, 20, 36)
        self.rightBtn.setStyleSheet("background-color: transparent;")
        self.rightBtn.setIcon(QIcon(str(self.imgDir / "right.png")))
        self.rightBtn.setIconSize(QSize(20, 36))
        self.rightBtn.clicked.connect(self.right)
        self.updateUI()
        self.closeBtn = QPushButton(self)
        self.closeBtn.setGeometry(448, 34, 24, 24)
        self.closeBtn.setStyleSheet("background-color: transparent;")
        self.closeBtn.setIcon(QIcon(str(self.imgDir / "close_w.png")))
        self.closeBtn.clicked.connect(self.close)
        self.second = QFrame(self)
        self.second.setGeometry(0, 640, 500, 226)
        self.second.setStyleSheet("background-color: white; border-bottom-left-radius: 16px; border-bottom-right-radius: 16px;")
        self.title = QLabel(self.second)
        self.title.setText("亲密度等级")
        self.title.setGeometry(30, 20, 140, 34)
        self.title.setStyleSheet(
            """
                QLabel { 
                    background-color: transparent;
                    color: #2c2c2c;
                    font-family: "Microsoft YaHei";
                    font-size: 28px;
                    line-height: 34px;
                    font-weight: bold;
                }
            """)
        self.levelLabel = QLabel(self.second)
        self.levelLabel.setGeometry(180, 24, 108, 28)
        self.levelImg = QPixmap(str(self.imgDir / f"level{self.maxLevel}.png"))
        self.levelLabel.setPixmap(self.levelImg)
        self.levelLabel.setScaledContents(True)
        self.intimacyLabel = QLabel(self.second)
        self.intimacyLabel.setGeometry(295, 60, 80, 34)
        self.intimacyLabel.setText(f"{self.intimacy * 10}/100")
        self.intimacyLabel.setStyleSheet(
            """
                QLabel { 
                    background-color: transparent;
                    color: #666666;
                    font-family: "Microsoft YaHei";
                    font-size: 24px;
                    line-height: 34px
                }
            """
        )
        self.baseColor = ["", "rgba(89, 185, 151, 0.2)", "rgba(45, 141, 250, 0.2)", "rgba(148, 118, 244, 0.2)"]
        self.barColor = ["", "rgb(89, 185, 151)", "rgb(45, 141, 250)", "rgb(148, 118, 244)"]
        self.baseBar = QFrame(self.second)
        self.baseBar.setGeometry(30, 70, 248, 12)
        self.baseBar.setStyleSheet(f"background-color: {self.baseColor[self.curCharacter]}; border-radius: 6;")
        self.bar = QFrame(self.second)
        if self.intimacy == 0: 
            self.barLen = 12
        elif self.intimacy > 10:
            self.barLen = 248
        else:
            self.barLen = int(self.intimacy * 24.8)
        self.bar.setGeometry(30, 70, self.barLen, 12)
        self.bar.setStyleSheet(f"background-color: {self.barColor[self.curCharacter]}; border-radius: 6;")
        self.initEnd = True
    def upgrade(self, newLevel):
        self.maxLevel = newLevel
        self.levelImg = QPixmap(str(self.imgDir / f"level{self.maxLevel}.png"))
        self.levelLabel.setPixmap(self.levelImg)
    def updateUI(self):
        if not self.initEnd:
            return
        self.profileImg = QPixmap(str(self.imgDir / f"profile_{self.curCharacter}.png"))
        self.profile.setPixmap(self.profileImg)
        self.baseBar.setGeometry(30, 70, 248, 12)
        self.baseBar.setStyleSheet(f"background-color: {self.baseColor[self.curCharacter]}; border-radius: 6;")
        if self.intimacy == 0:
            self.barLen = 12
        elif self.intimacy > 10:
            self.barLen = 248
        else:
            self.barLen = int(self.intimacy * 24.8)
        self.bar.setGeometry(30, 70, self.barLen, 12)
        self.bar.setStyleSheet(f"background-color: {self.barColor[self.curCharacter]}; border-radius: 6;")
        if self.curCharacter != self.selectedCharacter:
            self.selectBtn.show()
        else:
            self.selectBtn.hide()
        if self.curCharacter == 1:
            self.leftBtn.hide()
            if self.maxLevel > 1:
                self.rightBtn.show()
            else:
                self.rightBtn.hide()
        elif self.curCharacter == 2:
            self.leftBtn.show()
            if self.maxLevel > 2:
                self.rightBtn.show()
            else:
                self.rightBtn.hide()
        elif self.curCharacter == 3:
            self.leftBtn.show()
            self.rightBtn.hide()
    def left(self):
        self.curCharacter -= 1
        self.updateUI()
    def right(self):
        self.curCharacter += 1
        self.updateUI()
    def confirm(self):
        self.selectedCharacter = self.curCharacter
        self.change_signal.emit(self.selectedCharacter)
        self.selectBtn.hide()

class SwitchChacaterWidget(QWidget):
    selected = pyqtSignal(int)
    def __init__(self, parent: QWidget | None = ..., flags: Qt.WindowFlags | Qt.WindowType = ...) -> None:
        super().__init__(parent, flags)
        self.imgDir = settings.SETUP_DIR / "img"
        self.setGeometry(580, 420, 1256, 510)
        self.bg = QFrame(self)
        self.bg.setGeometry(0, 0, 1256, 510)
        self.bg.setStyleSheet("background-color: white; border-radius: 16px")
        self.title = QLabel(self)
        self.title.setGeometry(40, 36, 300, 60)
        self.title.setText("切换角色")
        self.title.setStyleSheet("font-size: 48px; font-weight: bold; font-family: 'Microsoft YaHei';")
        self.closeBtn = QPushButton(self)
        self.closeBtn.setGeometry(1170, 36, 26, 26)
        self.closeBtn.setStyleSheet("background-color: transparent;")
        self.closeBtn.setIcon(QIcon(str(self.imgDir / "close_b.png")))
        self.closeBtn.clicked.connect(self.close)
        
        images = [self.imgDir / "1.png", self.imgDir / "2.png", self.imgDir / "3.png"]
        self.image1 = QPushButton(self)
        self.image1.setGeometry(50, 130, 350, 350)
        self.image1.setIcon(QIcon(str(images[0])))
        self.image1.setIconSize(QSize(350, 350))
        self.image1.setStyleSheet("background-color: transparent;")
        self.image1.clicked.connect(self.select1)
        self.image2 = QPushButton(self)
        self.image2.setGeometry(450, 130, 350, 350)
        self.image2.setIcon(QIcon(str(images[1])))
        self.image2.setIconSize(QSize(350, 350))
        self.image2.setStyleSheet("background-color: transparent;")
        self.image2.clicked.connect(self.select2)
        self.image3 = QPushButton(self)
        self.image3.setGeometry(850, 130, 350, 350)
        self.image3.setIcon(QIcon(str(images[2])))
        self.image3.setIconSize(QSize(350, 350))
        self.image3.setStyleSheet("background-color: transparent;")
        self.image3.clicked.connect(self.select3)
        
    def select1(self):
        self.selected.emit(1)
        self.close()
    def select2(self):
        self.selected.emit(2)
        self.close()
    def select3(self):
        self.selected.emit(3)
        self.close()


class ResetWidget(QWidget):
    confirm_reset = pyqtSignal()
    def __init__(self, parent: QWidget | None = ..., flags: Qt.WindowFlags | Qt.WindowType = ...) -> None:
        super().__init__(parent, flags)
        self.setObjectName("ResetWidget")
        self.setGeometry(0 + 1600, 330, 560, 280)
        self.bg = QFrame(self)
        self.bg.setGeometry(0, 0, 560, 280)
        self.bg.setStyleSheet("background-color: white; border-radius: 16px")
        self.title = QLabel("重置对话", self)
        self.title.setGeometry(48, 32, 128, 38)
        self.title.setStyleSheet("color: #222222; font-family: 'Microsoft YaHei'; font-weight: bold; font-size: 32px; line-height: 38px;")
        self.subTitle = QTextEdit("重置后你与小龙的聊天记忆会被清空，下次你们将重新认识", self)
        self.subTitle.setGeometry(48, 100, 460, 68 + 10)
        self.subTitle.setEnabled(False)
        self.subTitle.setStyleSheet(
            """
                QTextEdit { 
                    background-color: transparent;
                    color : #666666;
                    font-family: "Microsoft YaHei";
                    font-size: 28px;
                    line-height: 34px;
                    border: none;
                }
            """
        )
        self.subTitle.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cancelBtn = QPushButton("取消", self)
        self.cancelBtn.setGeometry(240, 200, 128, 48)
        self.cancelBtn.setStyleSheet("background-color: transparent; border-radius: 8px; border: 1px solid #d9d9d9; color: #222222; font-family: 'Microsoft YaHei'; font-size: 24px; line-height: 28px;")
        self.cancelBtn.clicked.connect(self.close)
        self.confirmBtn = QPushButton("重置", self)
        self.confirmBtn.setGeometry(384, 200, 128, 48)
        self.confirmBtn.setStyleSheet("background-color: #222222; border-radius: 8px; color: #ffffff; font-family: 'Microsoft YaHei'; font-size: 24px; line-height: 28px;")
        self.confirmBtn.clicked.connect(self.reset)
    
    def reset(self):
        print("reset")
        self.confirm_reset.emit()
        self.close()

class UpgradeWidget(QWidget):
    def __init__(self, parent: QWidget | None = ..., flags: Qt.WindowFlags | Qt.WindowType = ...) -> None:
        super().__init__(parent, flags)
