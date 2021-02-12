from py4j.java_gateway import JavaGateway, GatewayParameters
from py4j.protocol import Py4JNetworkError
import subprocess,socket
import struct,serial
from Mini4WDException import NoPortOpendeException,DutyRatioException,InvalidDutyMap
import csv

class Mini4WDHandler():
    '''
    
    Mini4WDのduty比やら接続やらを扱う
    Parameters
    ----------
    M4DIr:Mini4WDInitializer
        システム初期化インスタンス(設定ファイルから値を呼び出し，書き込むインスタンス)
    M4DJH:Mini4WDJavaHandler
        Javaと通信を行うためのハンドラー
    X:int
        ミニ四駆のXエリア
    Y:int
        ミニ四駆のYエリア
    DivMapH:int
        DutyMapの縦の分割数
    DivMapW:int
        DutyMapの横の分割数
    InitializeDutyRatio:float
            DutyMapにおける初期化時の初期値
    DutyMap:array-like
        指定された分割数とduty比に基づいてDuty比を記録するマップ(二次元配列)
    app:entry_Point
        Javaプログラムのインスタンス

    Throws
    ------
    KeyError:
        settingファイルの構文が間違っている

    Attension
    ---------
    Pythonは型宣言をしないので，渡す変数の方には最上級の注意を払うこと．特にGateway Serverはエラーを
    吐かないので，うまく起動しないときは

    JVMとパイソンの間でのポート番号があっているか
    Mini4WD本体と通信するためのポート名があっているか
    Mini4WDがすでに起動しているかどうか

    これらに気を使う必要がある

    '''

    def __init__(self,Mini4WDLogger):
        '''

        Parameters
        ----------
        Mini4WDDetector:Mini4WDDetector()
            クラスMini4WDDetectorのインスタンス
        Error
            ポートが使えないというエラー
            もしくは指定されたワークスペースが間違っている

        '''
        
        self.M4DL                   = Mini4WDLogger
        self.M4DIr                  = self.M4DL.GetM4DIr()
        self.M4DJH                  = Mini4WDJavaHandler(self.M4DIr.GetFileValue('M4DSClassPath'),\
                                        self.M4DIr.GetFileValue('M4DSClassName'),\
                                        self.M4DIr.GetFileValue('M4DSPortNum'),\
                                        self.M4DIr.GetFileValue('Mini4WDPortName'),\
                                        self.M4DL.GetLogFileName())
        self.X                      = 0
        self.Y                      = 0
        self.DivMapH                = 0
        self.DivMapW                = 0
        self.InitializeDutyRatio    = float(self.M4DIr.GetFileValue('InitializeDutyRatio'))
        self.M4DM                   = Mini4WDDutyMap(self)
        self.M4DM.ApplyCSVFileWithDmap(self.M4DIr.GetFileValue('CSVFilePath'))
        self.app                    = self.M4DJH.GetApp()
        self.currentDutyRatio       = 0

    def __del__(self):
        '''
        ミニ四駆を停止させる．
        '''
        self.offRightLED()
        self.offLeftLED()
        self.SendDutyCommand(0)

    def InitializeDutyMap(self,InitializeDutyRatio=0):
        '''

        DutyMapを引数をもとに初期化する

        Parametars
        ----------
        InitializeDutyRatio:float default=0
            DutyMapを初期化するときのすべてのエリアにおける初期値

        Returns
        -------
        DutyMap:int array[2]
            どのエリアでどれくらいのDuty比にするのかを決めた配列．

        '''
        self.InitializeDutyRatio=InitializeDutyRatio
        DutyMap=list()
        temp=list()
        for i in range(0,self.DivMapH):
            # temp=list()
            for j in range(0,self.DivMapW):
                temp.append(self.InitializeDutyRatio)
            DutyMap.append(temp)
            temp=list()
        return DutyMap

    def GetDivMapH(self):
        '''
        エリアの縦の分割数を取得する
        Returns
        -------
        DivMapH:int
            エリアの縦の分割数
        '''
        return self.DivMapH

    def GetDivMapW(self):
        '''
        エリアの横の分割数を取得する
        Returns
        -------
        DivMapW:int
            エリアの横の分割数
        '''
        return self.DivMapW

    def GetOpenPortNum(self):
        '''
        Deprecated
        ----------

        25335=65335の間で空きポート番号を取得する
        割と時間がかかるから実行の際は注意すべし
        あまりにも遅すぎるからとりあえず使わない．

        Returns
        -------
        PortNum:int
            空きポート番号.
            -1ならばどのポートも開いていなかったことになる

        Throws
        ------
        NoPortOpendeException:
            どこのポートも空いていない場合の例外

        '''
        for PortNum in range(25333, 65535):
            #target_host のポート番号portに接続を試行
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            return_code = sock.connect_ex(('localhost', PortNum))
            if return_code == 0 :
                sock.close() #socket.connect_ex は成功すると0を返す
                return PortNum
            sock.close() #socket.connect_ex は成功すると0を返す
        raise NoPortOpendeException

    def LocationChangeEventListner(self,X,Y):
        '''
        
        ミニ四駆のエリアの変化を検知したら呼び出されるイベントリスナー
        Mini4駆が存在するエリアにおけるDuty比を送信する
        
        Parameters
        ----------
        X:int
            Duty比を変えるエリアのX
        Y:int
            Duty比を変えるエリアのY
        '''
        newDutyRatio = self.M4DM.GetDutyRatio(X,Y)
        if newDutyRatio != self.currentDutyRatio:
            self.SendDutyCommand(newDutyRatio)
            self.currentDutyRatio = newDutyRatio
        
    def SendDutyCommand(self,dutyRatio):
        '''
        
        Duty比をMini4WDに送信する

        Parameters
        ----------
        DutyRatio:float
            指定したDuty比を送信する
        '''
        try:
            self.app.SendDutyCommand(dutyRatio)
        except Exception as e:
            print(e)

    def SetDivMapH(self, h):
        self.DivMapH = h

    def SetDivMapW(self, w):
        self.DivMapW = w

    def GetM4DM(self):
        return self.M4DM

    def GetM4DIr(self):
        return self.M4DIr

    def GetM4DL(self):
        return self.M4DL

    def onRightLED(self):
        try:
            self.app.onRightLED()
        except Py4JNetworkError as e:
            print(e)

    def offRightLED(self):
        try:
            self.app.offRightLED()
        except Py4JNetworkError as e:
            print(e)

    def onLeftLED(self):
        try:
            self.app.onLeftLED()
        except Py4JNetworkError as e:
            print(e)

    def offLeftLED(self):
        try:
            self.app.offLeftLED()
        except Py4JNetworkError as e:
            print(e)

class Mini4WDDutyMap():
    def __init__(self,M4DH):
        self.DutyMap=list()
        self.M4DH = M4DH
   
    def ApplyCSVFileWithDmap(self,filepath):
        self.DutyMap=list()
        Flag = True
        with open(filepath, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                w = len(row)
                if Flag:
                    pw = w
                    Flag = False
                
                if w != pw:
                    raise InvalidDutyMap

                temp = list()
                for value in row:
                    DutyRatio = float(value)
                    temp.append(DutyRatio)
                    if DutyRatio > 1 or DutyRatio < -1:
                        raise DutyRatioException

                self.DutyMap.append(temp)
            print(pw,reader.line_num)
            self.M4DH.SetDivMapW(pw)                # pwは一列目のduty比の数
            self.M4DH.SetDivMapH(reader.line_num)   # line_numはreaderが今まで読み込んだ行数

    def GetDutyRatio(self,X,Y):
        return self.DutyMap[Y][X]

    def GetDutyMap(self):
        '''
        DutyMapを返す

        Returns
        -------
        DutyMap:array_like
            duty比が入ったマップ

        '''
        return self.DutyMap

    def SetDutyRatio(self,X,Y,DutyRatio):
        '''
        
        指定された場所におけるミニ四駆のDuty比を変更する

        Parameters
        ----------
        X:int
            DutyMapの縦の番号
        Y:int
            DutyMapの横の番号
        DutyRatio:float or int
            Duty比の値

        Throws
        ------
        DutyRatioException:
            Duty比が1より大きいか-1より小さいかで投げられる例外
        IndexError:
            DutyMapで指定した座標が存在しません．

        '''
        if DutyRatio > 1 or DutyRatio < -1:
            raise DutyRatioException
        else:
            self.DutyMap[Y][X] = DutyRatio

    def SaveDutyMapAsCSV(self,filepath):
        with open(filepath, 'wt', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.DutyMap)

class Mini4WDJavaHandler():
    '''
    Javaクラスファイルとの中間役を果たすもの

    Parameters
    ----------
    Process:subprocess.Popen
        サブプロセスのインスタンス

    '''

    def __init__(self,ClassPath='',ClassName='',PortNum=25333,PortName='COM4',LogFileName=''):
        '''

        Parameters
        ----------
        ClassPath:String default=''
            Javaクラスファイル「まで」のパス
            Java ClassFile Path
        ClassName:String default=''
            Javaクラスファイルの名前
            Java ClassFile Name
        PortNum:int default=25333
            通信を行うポート番号
        PortName:String default='COM4'
            ミニ四駆と通信を行うBluetoothのポートの名前

        Throws
        ------
        Error
            ポートが使えないというエラー
            もしくは指定されたワークスペースが間違っている

        '''
        self.ClassPath  = ClassPath
        self.ClassName  = ClassName
        self.PortNum    = PortNum
        self.PortName   = PortName
        self.LogFileName = LogFileName
        self.Process    = None
        self.StartJava()
    
    def __del__(self):
        '''
        終了するときにこのインスタンス自体の子プロセスをkillする
        '''
        self.StopJava()

    def StartJava(self):
        '''
        指定したポートナンバーで，指定されたJavaプログラムを起動する

        Throws
        ------
        Error
            ポートが使えないというエラー
            もしくは指定されたワークスペースが間違っている
        '''

        # クラスパスを指定して実行
        print('Javaプログラムを始動します')
        args=(["java","-classpath",self.ClassPath,self.ClassName,str(self.PortNum),self.PortName,self.LogFileName])
        print(args)
        self.Process=subprocess.Popen(args)

        try:
            self.Process.wait(timeout=3)        #JVMが起動するまで待つ
        except subprocess.TimeoutExpired as e:  #この例外は必ず発生する
            pass
        except Exception:
            self.Process.kill()
            return(Exception)
        Gateway                 = JavaGateway(gateway_parameters=GatewayParameters(port=int(self.PortNum)))  # connect to the JVM
        app                     = Gateway.entry_point
        self.app                = app
        print('Javaプログラムを正常に始動しました！')

    def StopJava(self):
        '''
        
        Javaプログラムを停止させる

        Throws
        ------
        Error
            ポートが使えないというエラー
        KeyError
            指定されたJavapプログラムが保存されていないというエラー

        '''

        print(self.ClassName,'を止めます')
        self.app.CloseCSVFile()
        self.Process.kill()

    def GetApp(self):
        '''
        
        Javaプログラムのエントリーポイントとなる．これがJavaプログラムのインスタンスになる

        Returns
        -------
        app:entry_point
            Javaプログラムのインスタンス

        '''
        return self.app

class Mini4WDHandlerForTest(Mini4WDHandler):
    def __init__(self,Mini4WDLogger):

        '''

        Parameters
        ----------
        Mini4WDDetector:Mini4WDDetector()
            クラスMini4WDDetectorのインスタンス
        Error
            ポートが使えないというエラー
            もしくは指定されたワークスペースが間違っている

        '''
        self.M4DL               = Mini4WDLogger
        self.M4DIr              = self.M4DL.GetM4DIr()
        self.X                  = 0
        self.Y                  = 0
        self.DivMapH            = 0
        self.DivMapW            = 0
        self.M4DM               = Mini4WDDutyMap(self)
        self.M4DM.ApplyCSVFileWithDmap(self.M4DIr.GetFileValue('CSVFilePath'))
        self.currentDutyRatio   = 0

    def __del__(self):
        pass
    
    def SendDutyCommand(self, DutyRatio):
        print('SendDutyRatioが呼ばれました',DutyRatio)

    def GetM4DM(self):
        return self.M4DM
        