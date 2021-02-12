import cv2
import time,os
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from Mini4WDImage import Mini4WDImageProcessor
from Mini4WDException import NotAllowedValue,InvalidOperation,InvalidImageFile,CameraIsNotOpened,FailedCapturingBGSI

class Mini4WDDetector():

    '''
    
    ここではミニ四駆を見つけ，そのエリアを返却するモジュールを作成する．
    同時に，その映像を出力するプログラムも書く．
    変数の命名規則はアッパーキャメルケースで書いた．

    Attributes
    ----------
    M4DIP:Mini4WDImageprocessor
        ミニ四駆の画像の処理を行うクラスのインスタンス
    USBCamera:cv2.VideoCapture()
            読み込むUSBカメラもしくは映像
    BackGroundImage:array_like
        numpy型として保存した背景画像
    Mini4WDMinSize:int
        ミニ四駆とみなす最小のピクセル数
    Mini4WDMaxSize:int
        ミニ四駆とみなす最大のピクセル数
    DivMapH:int
        画像を縦にエリア分けする数
    DivMapW:int
        画像を縦にエリア分けする数
    VideoFrame:Mini4WDImage, default=None
        Cameraから読み込んだ1フレーム
    binaryImage:array_like
        作成した二値画像のnumpy配列
    StartFlag:boolean default=False
        ミニ四駆の検知を行うかどうかのフラグ
    mapX:int
        分割したマップにおけるミニ四駆の横のエリアの番号
    mapY:int
        分割したマップにおけるミニ四駆の縦のエリアの番号
    xCoordinate:int
        ミニ四駆が位置する領域の中心x座標
    yCoordinate:int
        ミニ四駆が位置する領域の中心y座標
    wLength:int
        検出したミニ四駆の横の長さ
    hLength:int
        検出したミニ四駆の縦の長さ
    mapArea:int
        画像におけるミニ四駆のピクセル数を示す．
        ただしこれは検出した領域で囲まれるピクセルの数
    '''

    def __init__(self,Mini4WDHandler):
        '''
        初期化を行う．
        Parameters
        ----------
        M4DIr:Mini4WDInitializer
            ミニ四駆の初期設定ファイルを扱うインスタンス
        M4DH:Mini4WDHandler
            ミニ四駆に信号を送るインスタンス
        '''
        self.M4DH               = Mini4WDHandler
        self.M4DIr              = self.M4DH.GetM4DIr()
        self.M4DL               = self.M4DH.GetM4DL()
        self.M4DIP              = Mini4WDImageProcessor(self.M4DIr,self.M4DH)
        self.BackGroundImage    = None
        self.BGSIPath           = self.M4DIr.GetFileValue('BGSIPath')
        self.USBCamera          = cv2.VideoCapture(int(self.M4DIr.GetFileValue('USBCameraNum')))
        self.Mini4WDMaxSize     = int(self.M4DIr.GetFileValue('Mini4WDMaxSize'))
        self.Mini4WDMinSize     = int(self.M4DIr.GetFileValue('Mini4WDMinSize'))
        self.DivMapH            = self.M4DH.GetDivMapH()
        self.DivMapW            = self.M4DH.GetDivMapW()
        self.VideoFrame         = None
        self.binaryImage        = None
        self.StartFlag          = False
        self.ShowFlag           = False
        self.mapX               = 0
        self.mapY               = 0
        self.xCoordinate        = 0
        self.yCoordinate        = 0
        self.wLength            = 0
        self.hLength            = 0
        self.mapArea            = 0
        self.SetBGSI()

    def __del__(self):
        '''
        USBカメラの解放とShowVideoで作成したウィンドウの削除．
        '''
        if self.USBCamera.isOpened():
            self.USBCamera.release()
            os.remove(self.BGSIPath)
        cv2.destroyAllWindows()

    def DetectMini4WD(self,BackGroundImage,VideoFrame,gx_pre,gy_pre):
        '''
        背景画像とビデオフレームを一枚ずつ取得し，前回のミニ四駆の
        座標を用いつつ今回のミニ四駆の座標を推定する．

        Parameters
        ----------
        BackGrounImage:array_like
            すでに適切に画像処理した後のnumpy配列の背景画像
        VideoFrame:array_like
            すでに適切に画像処理した後のnumpy配列のUSBカメラ画像
        gx_pre:int
            前回のミニ四駆の場所
        gy_pre:int
            前回のミニ四駆の場所

        Returns
        -------
        x:int
            ミニ四駆の外接短形の左上の点のx座標．
            ミニ四駆未発見時は-1
        y:int
            ミニ四駆の外接短形の左上の点のx座標
            ミニ四駆未発見時は-1
        w:int
            ミニ四駆の外接短形の横の長さ
            ミニ四駆未発見時は-1
        h:int
            ミニ四駆の外接短形の縦の長さ
            ミニ四駆未発見時は-1
        gx:int
            ミニ四駆のX座標
            ミニ四駆未発見時は-1
        gy:int
            ミニ四駆のY座標
            ミニ四駆未発見時は-1
        maparea:int
            画像上におけるミニ四駆の面積
            ミニ四駆未発見時は-1

        '''
        IsMini4WD                                   = False
        rectlist                                    = []
        gdlist                                      = []
        x = y = w = h = gx = gy = area = maparea    = -1

        # 背景差分をとる
        fgbg                = cv2.bgsegm.createBackgroundSubtractorMOG()#背景オブジェクトの作成
        fgmask              = fgbg.apply(BackGroundImage)#領域の適用
        fgmask              = fgbg.apply(VideoFrame)
        self.binaryImage    = fgmask

        #ピクセル数を数える
        contours, hierarchy = cv2.findContours(self.binaryImage, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # 各輪郭に対する処理
        for i in range(0, len(contours)):

            # 輪郭の領域を計算
            area = cv2.contourArea(contours[i])

            # ノイズ（小さすぎる領域）と全体の輪郭（大きすぎる領域）を除外
            # if area < self.Mini4WDMinSize or self.Mini4WDMaxSize < area:
            #     continue

            # 外接矩形
            if len(contours[i]) > 0:
                x, y, w, h  = cv2.boundingRect(contours[i])
                gx          = x+w/2
                gy          = y+h/2
                rect        = (x, y, w, h, gx, gy, area)
                gd          = (gx-gx_pre)*(gx-gx_pre)+(gy-gy_pre)*(gy-gy_pre)
                maparea     = area    
                rectlist.append(rect)
                gdlist.append(gd)
                if gd < 20:
                    IsMini4WD = True
                # print(x, y, w, h, gx, gy, maparea)
                
        if IsMini4WD:
            x, y, w, h, gx, gy, maparea = rectlist[gdlist.index(min(gdlist))]
            # print(x, y, w, h, gx, gy, maparea)
        
        return x, y, w, h, gx, gy, maparea

    def GetInformationsOfDetection(self):
        '''
        ミニ四駆検知で得られた情報を返却する
        Returns
        -------
        mapX:int
            分割したマップにおけるミニ四駆の横のエリアの番号
        mapY:int
            分割したマップにおけるミニ四駆の縦のエリアの番号
        xCoordinate:int
            ミニ四駆が位置する領域の中心x座標
        yCoordinate:int
            ミニ四駆が位置する領域の中心y座標
        wLength:int
            検出したミニ四駆の横の長さ
        hLength:int
            検出したミニ四駆の縦の長さ
        mapArea:int
            画像におけるミニ四駆のピクセル数を示す．
            ただしこれは検出した領域で囲まれるピクセルの数
        '''
        return self.mapX ,self.mapY, self.xCoordinate,self.yCoordinate,\
            self.wLength,self.hLength,self.mapArea

    def GetMini4WDXYCoordinates(self):
        '''
        ミニ四駆の座標を取得する

        Returns
        -------
        xCoordinate:int
            ミニ四駆が位置する横の座標を返す
        yCoordinate:int
            ミニ四駆が位置する縦の座標を返す

        '''
        return self.xCoordinate,self.yCoordinate

    def GetMini4WDLocation(self):
        '''
        ミニ四駆のマップ上のエリアを示す．

        Returns
        -------
        mapX:int
            ミニ四駆が位置するエリアの横の番号を返す
        mapY:int
            ミニ四駆が位置するエリアの縦の番号を返す

        '''
        return self.mapX,self.mapY    

    def GetMini4WDMaxSize(self):
        '''
        ミニ四駆だと判断する最大面積を返す．

        Returns
        -------
        Mini4WDMaxSize:int
            ミニ四駆だと判断する最大面積
        '''
        return self.Mini4WDMaxSize

    def GetMini4WDMinSize(self):
        '''
        ミニ四駆だと判断する最小面積を返す．

        Returns
        -------
        Mini4WDMinSize:int
            ミニ四駆だと判断する最小面積
        '''
        return self.Mini4WDMinSize

    def GetBackGroundImage(self):
        '''
        背景画像のインスタンスを返す.

        Returns
        -------
        BackGrounImage:array_like
            背景画像のインスタンス．
        '''
        return self.BackGroundImage

    def GetVideoFrame(self):
        '''
        VideoFrameインスタンスを返す

        Returns
        -------
        VideoFrame:Mini4WDVideoFrame
            USBカメラから取得した1フレームの
            のインスタンス
        '''
        return self.VideoFrame

    def SaveBackGroundSubstractorImage(self, pathname):
        '''
        今現在持っている背景画像の保存

        Parameters
        ----------
        pathname:String
            保存先のパス

        '''
        cv2.imwrite(pathname,self.BackGroundImage)

    def SetBGSI(self):
        '''
        現在のカメラから背景画像を適切に取得する．
        カメラはパラメータを自動調整するので，それが終了したら背景画像を取得する
        '''
        if self.USBCamera.isOpened():
            print('背景画像の自動調節中です...')
            ret, frame1 = self.USBCamera.read()
            frame1 = self.M4DIP.ImagePreprocessing(frame1)
            scount = 0
            fcount = 0

            # 背景差分をとる
            while True:
                ret, frame2 = self.USBCamera.read()
                frame2      = self.M4DIP.ImagePreprocessing(frame2)
                fgbg                = cv2.bgsegm.createBackgroundSubtractorMOG()#背景オブジェクトの作成
                fgmask              = fgbg.apply(frame1)#領域の適用
                fgmask              = fgbg.apply(frame2)
                contours, hierarchy = cv2.findContours(fgmask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                frame1 = frame2
                if len(contours) > 0:
                    scount = 0
                    fcount += 1
                    if fcount > 180: # 合計で6秒以上連続して失敗した場合は
                        raise FailedCapturingBGSI
                    continue
                else :
                    scount += 1
                    if scount > 45:
                        break

            # 最後のフレームを背景画像としてセットする
            self.BackGroundImage = frame1
            cv2.imwrite(self.BGSIPath,self.BackGroundImage)

            print('背景画像の自動調節が終了しました!')

        else :
            raise CameraIsNotOpened

    def GetBGSIPath(self):
        return self.BGSIPath

    def SetInformationsOfDetection(self,mapX,mapY,xCoordinate,yCoordinate,wLength,hLength,mapArea):
        '''
        ミニ四駆検知で得られた様々な情報をこのMini4WDDetectorインスタンス
        に設定する．

        Parameters
        ----------
        mapX:int
            分割したマップにおけるミニ四駆の横のエリアの番号
        mapY:int
            分割したマップにおけるミニ四駆の縦のエリアの番号
        xCoordinate:int
            ミニ四駆が位置する領域の中心x座標
        yCoordinate:int
            ミニ四駆が位置する領域の中心y座標
        wLength:int
            検出したミニ四駆の横の長さ
        hLength:int
            検出したミニ四駆の縦の長さ
        mapArea:int
            画像におけるミニ四駆のピクセル数を示す．
            ただしこれは検出した領域で囲まれるピクセルの数

        Throws
        ------
        NotAllowedValue:
            不正な数値が指定された場合，この例外を投げる．

        '''

        if mapX<0 or mapX>self.DivMapW-1 or mapY<0 or mapY>self.DivMapH-1 or\
            xCoordinate<0 or xCoordinate>self.BackGroundImage.shape[1] or\
            yCoordinate<0 or yCoordinate>self.BackGroundImage.shape[0] or\
            wLength<0 or hLength<0 :
            # or mapArea>self.Mini4WDMaxSize or mapArea<self.Mini4WDMinSize:
            print(mapX,mapY,xCoordinate,yCoordinate,wLength,hLength,mapArea)
            raise NotAllowedValue

        self.mapX       = mapX
        self.mapY       = mapY
        self.xCoordinate= xCoordinate
        self.yCoordinate= yCoordinate
        self.wLength    = wLength
        self.hLength    = hLength
        self.mapArea    = mapArea

    def StopDetectingMini4WD(self):
        '''
        ミニ四駆を検知するか否かを示すフラグを偽にして，
        ミニ四駆の検知が始まっている場合，それを止める．
        '''
        if self.StartFlag == False:
            raise InvalidOperation
        self.StartFlag = False

    def StartDetectingMini4WD(self):
        '''
        USBカメラが使用可能でかつフラグがTrueのときミニ四駆の検知を始める.
        multiprocessingなどの並行処理で呼び出すことで，Restartさせることが
        可能．
        '''
        #プロパティの宣言-----------------------------#
        # ミニ四駆を一番初めに設置したエリア -> 1フレーム前のエリア
        # この場合は初期設定ファイルから読み込む
        mapX_pre,mapY_pre                       = int(self.M4DIr.GetFileValue('mapX_pre')),int(self.M4DIr.GetFileValue('mapY_pre'))
        self.M4DH.LocationChangeEventListner(mapX_pre,mapY_pre)
        # ミニ四駆を一番初めに設置したエリアの座標 -> 1フレーム前のミニ四駆の座標
        gx_pre , gy_pre                         = (self.BackGroundImage.shape[1]/self.DivMapW)//2*(mapX_pre+1), (self.BackGroundImage.shape[0]/self.DivMapH)//2*(mapY_pre+1)
        self.StartFlag                          = True
        #--------------------------------------------#

        while(self.USBCamera.isOpened() & self.StartFlag):
            ret, frame  = self.USBCamera.read()                                 # VideoCaptureから1フレーム読み込む

            if(ret):
                self.VideoFrame     = self.M4DIP.ImagePreprocessing(frame)     # ここでビデオフレームの前処理を行う
                x,y,w,h,gx,gy,area  = \
                    self.DetectMini4WD(self.BackGroundImage,self.VideoFrame,gx_pre,gy_pre)# ミニ四駆の検知
                
                if gx == -1:                                                    # もし見つからなかったら
                    continue                                                    # 次のループへ
                
                mapX                 = int(gx//(self.VideoFrame.shape[1]//self.DivMapW))
                mapY                 = int(gy//(self.VideoFrame.shape[0]//self.DivMapH))
                # print(mapX,mapY)
                self.SetInformationsOfDetection(mapX,mapY,gx,gy,w,h,area)
                self.M4DL.AppendDetectionLog(self.GetInformationsOfDetection())
                if mapX!=mapX_pre or mapY!=mapY_pre:
                    self.M4DH.LocationChangeEventListner(mapX,mapY)
                    mapX_pre=mapX
                    mapY_pre=mapY
                    
                gx_pre,gy_pre        = gx,gy                                         # 次の呼び出しのために値渡し

                # showFlagがTrueなら下記の処理をする（本来は）
                if True:
                    cv2.imshow('USBCamera',self.VideoFrame)
                    cv2.imshow('Binary',self.binaryImage)
                    k = cv2.waitKey(1)

        cv2.destroyAllWindows()
        return
    
    def ShowFrame(self):
        self.ShowFlag=True

    def CloseFrame(self):
        self.ShowFlag = False
        cv2.destroyAllWindows()

    def RestartDetectingMini4WD(self):
        '''
        ミニ四駆検知を再始動させる．
        '''
        if self.StartFlag:
            raise InvalidOperation
        self.StartFlag = True

    def GetM4DIP(self):
        return self.M4DIP

    def GetM4DH(self):
        return self.M4DH

    def GetM4DIr(self):
        return self.M4DIr

    def GetM4DL(self):
        return self.M4DL
