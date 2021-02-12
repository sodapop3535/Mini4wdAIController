from Mini4WDDetector import Mini4WDDetector
from Mini4WDInitializer import Mini4WDInitializer
from Mini4WDLogger import Mini4WDLogger
from Mini4WDHandler import Mini4WDHandler,Mini4WDHandlerForTest
from Mini4WDGUI import Mini4WDGUI
import Mini4WDException
import wx

def main():
    # 初期設定
    M4DIr   = Mini4WDInitializer('./.setting')      # 初期設定を呼び出す者
    M4DL    = Mini4WDLogger(M4DIr)                  # ログをとるクラスのインスタンス
    M4DH    = Mini4WDHandler(M4DL)                  # Mini4WDを制御する者
    # M4DH    = Mini4WDHandlerForTest(M4DL)         # Mini4WDを制御する者
    M4DD    = Mini4WDDetector(M4DH)                 # Mini4WDを発見する者
    
    # GUIの起動
    app     = wx.App()
    M4DG    = Mini4WDGUI(None)
    M4DG.ini_frame(M4DD)
    app.MainLoop()

if __name__ == "__main__":
    main()
