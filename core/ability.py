import os
import subprocess
import time
import schedule
import winreg
import win32gui
import win32gui, win32ui
from ctypes import windll
from PyQt5.QtCore import QThread
from core.upload_img import uploadImage
from core.conf import settings

class Ability(object):
    def __init__(self):
        self.system = os.name
        self.cnt = 0

    def openBMW(self):
        steamPath = self.getSteamPath()
        gamePath = steamPath + '\\steamapps\\common\\BlackMythWukong\\b1\\Binaries\\Win64\\b1-Win64-Shipping.exe'
        subprocess.Popen([gamePath])
        schedule.every(5).seconds.do(self.getScreenShot)
        self.thread = Thread(app='screenShot')
        self.thread.start()
        
    def getScreenShot(self):
        try:
            hwnd = win32gui.FindWindow(None, 'b1  ')
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            left, top, right, bot = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bot - top
            
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
            filename = f"{settings.SETUP_DIR}\\output\\screenshot_{self.cnt}.jpg"
            saveBitMap.SaveBitmapFile(saveDC, filename)

            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            time.sleep(1)
            uploadImage(filename)

            print(self.cnt)
            self.cnt += 1
        except Exception as e:
            print(f"GetScreenShot Error: {e}")
    def getSteamPath(self):
        try:
            reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(reg, r"SOFTWARE\WOW6432Node\Valve\Steam")
            steam_path, _ = winreg.QueryValueEx(key, "InstallPath")
            winreg.CloseKey(key)
            return steam_path
        except FileNotFoundError:
            return "Steam installation path not found in registry"


class Thread(QThread):
    def __init__(self, app=None):
        super(Thread, self).__init__()
        self.app = app

    def run(self):
        if self.app == 'screenShot':
            time.sleep(15)
            while True:
                schedule.run_pending()
                time.sleep(1)
