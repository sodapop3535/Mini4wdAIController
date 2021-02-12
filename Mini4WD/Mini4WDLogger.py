import time
import os
import csv
import threading

class Mini4WDLogger:
    def __init__(self,M4DIr):
        self.M4DIr                  = M4DIr
        self.AreLogsLeft            = True                                                              # 作成したログを消すか否か
        self.logFolderPath          = self.M4DIr.GetFileValue('LogFolderPath')
        self.stime                  = time.strftime("%Y%m%d%H%M%S", time.localtime())                      # 日付の取得
        self.LogFileName            = self.logFolderPath+self.stime+'/'+self.stime
        os.mkdir(self.logFolderPath+self.stime)                                                              # ログフォルダを作成する．
        self.operationLogFile       = self.createFile(self.LogFileName+'_operation.txt')   # オペレーションログファイルを作成する．
        # self.mini4WDSensorLogFile   = self.createFile(self.LogFileName+'_sensor.csv')   # センサーログファイルを作成する．
        self.detectionLogFile       = None                                                              # ミニ四駆検知ログファイル（初期値はNone）
        self.dcount                 = 0
        self.scount                 = 0
        self.drow                   = 0
        self.detectionLog           = list()
        self.sensorLog              = list()

    def __del__(self):
        '''
        作成したすべてのファイルを適切にクローズする.
        LeaveFlagがFalseの場合，ログをすべて消す．
        '''
        self.WriteOperationLog('Mini4WD Controler is stopped.')
        self.operationLogFile.close()
        # self.WriteMini4WDSensorLog()
        # self.mini4WDSensorLogFile.close()

        if self.detectionLogFile is not None:
            self.WriteDetectionLog()
            self.detectionLogFile.close()

        if self.AreLogsLeft is False:
            os.remove(self.logFolderPath+self.stime)

    def createFile(self,filename):
        '''
        ログファイルを作る

        Returns
        -------
        fout:os.file
            ファイルのインスタンス

        '''
        try:
            fout = open(filename,'at',newline="")
        except IOError as e:
            print(e)
            exit()
        return fout

    def WriteOperationLog(self,line):
        '''
        操作ログに記録する．
        '''
        try:
            self.operationLogFile.write(time.strftime("%Y%m%d%H%M%S", time.localtime())+'\t' + line+'\n')
        except IOError as e:
            print(e)

    def AppendSensorLog(self,array):
        array = list(array)
        array.insert(0,time.time())
        self.sensorLog.append(array)
        self.scount += 1
        print(self.sensorLog)
        if self.scount == 1:
            print('書き込みます')
            thread = threading(target=self.WriteMini4WDSensorLog)
            self.scount = 0

    def WriteMini4WDSensorLog(self):
        '''
        センサーログに記録する
        '''
        try:
            cout = csv.writer(self.mini4WDSensorLogFile)
            if len(self.detectionLog)>1:
                cout.writerows(self.sensorLog)
            else :
                cout.writerow(self.sensorLog)
        except IOError as e:
            print(e)

    def AppendDetectionLog(self,array):
        array = list(array)
        array.insert(0,time.time())
        self.detectionLog.append(array)
        self.drow += 1                  # 関数呼び出しがいやだからこう書いている．でも速くなるかは不明
        if self.drow == 10000:
            thread = threading(target=self.WriteDetectionLog)
            self.drow = 0

    def WriteDetectionLog(self):
        '''
        ミニ四駆検知ログに記録する
        '''
        try:
            cout = csv.writer(self.detectionLogFile)
            if len(self.detectionLog)>1:
                cout.writerows(self.detectionLog)
            else :
                cout.writerow(self.detectionLog)
        except IOError as e:
            print(e)
        self.detectionLog = list()

    def UpdateDetectionLogFile(self):
        '''
        Detection Log Fileのみ，Detectionの実行ごとにファイルを書き換えるので，
        書き込むログファイルをアップデートする．
        '''
        if self.detectionLogFile is not None:
            self.WriteDetectionLog()
            self.detectionLogFile.close()
        self.dcount += 1
        self.detectionLogFile = open('{}_detection_{}.csv'\
            .format(self.LogFileName,self.dcount),'at',newline="")
        try:
            cout = csv.writer(self.detectionLogFile)
            cout.writerow(("time","mapX","mapY","xCoordinate","yCoordinate","wLength","hLength","mapArea"))
        except IOError as e:
            print(e)

    def GetDetectionLogFileNum(self):
        '''
        現在のログファイルの個数を返す
        '''
        return self.dcount

    def NotLeaveLogs(self):
        '''
        履歴を残させない．
        '''
        self.AreLogsLeft = False

    def LeaveLogs(self):
        '''
        履歴を残す
        '''
        self.AreLogsLeft = True

    def GetLogFileName(self):
        return self.LogFileName

    def GetM4DIr(self):
        return self.M4DIr
