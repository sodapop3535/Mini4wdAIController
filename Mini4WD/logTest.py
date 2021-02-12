from Mini4WDDetector import Mini4WDDetector
from Mini4WDInitializer import Mini4WDInitializer
from Mini4WDLogger import Mini4WDLogger
from Mini4WDHandler import Mini4WDHandler,Mini4WDHandlerForTest
from Mini4WDGUI import Mini4WDGUI
import Mini4WDException
from py4j.java_gateway import JavaGateway, CallbackServerParameters

def main():
    M4DIr   = Mini4WDInitializer('./.setting')      # 初期設定を呼び出す者
    M4DL    = Mini4WDLogger(M4DIr)                  # ログをとるクラスのインスタンス
    # M4DL.WriteOperationLog('test')
    # test=[2, 1, 260.5, 61.5, 3, 3, 2.5]
    
    # test2=[2, 1, 260.5, 62.5, 3, 3, 1.5]
    # M4DL.UpdateDetectionLogFile()
    # M4DL.WriteDetectionLog(test)
    # M4DL.WriteMini4WDSensorLog(test2)
    gateway = JavaGateway(
        callback_server_parameters=CallbackServerParameters(),
        python_server_entry_point=M4DL)

if __name__=='__main__':
    main()