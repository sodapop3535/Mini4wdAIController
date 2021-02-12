import time
import multiprocessing
import threading
import cv2
import numpy as np
from PIL import Image
from Mini4WDDetector import Mini4WDDetector
from Mini4WDInitializer import Mini4WDInitializer
from Mini4WDHandler import Mini4WDHandlerForTest
import Mini4WDException
from TestAndDemo.MeasureExecuteTime import stop_watch
from cMini4WDDetector import Mini4WDDetector as cMini4WDDetector

class Mini4WDDetectorForTest(Mini4WDDetector):
    def __init__(self,M4DIr,M4DH):
        super().__init__(M4DIr,M4DH)
        self.frameNum=0

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
        self.frameNum+=1
        IsMini4WD                       = False
        rectlist                        = []
        gdlist                          = []
        x = y = w = h = gx = gy = area = maparea  = -1

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
            if area < self.Mini4WDMinSize or self.Mini4WDMaxSize < area:
                continue

            # 外接矩形
            if len(contours[i]) > 0:
                x, y, w, h = cv2.boundingRect(contours[i])
                gx = x+w/2
                gy = y+h/2
                rect = (x, y, w, h, gx, gy, area)
                gd = (gx-gx_pre)*(gx-gx_pre)+(gy-gy_pre)*(gy-gy_pre)    
                rectlist.append(rect)
                gdlist.append(gd)
                IsMini4WD = True
                maparea = area
                # print(x, y, w, h, gx, gy, maparea)
                
        if IsMini4WD:
            x, y, w, h, gx, gy, maparea = rectlist[gdlist.index(min(gdlist))]
        
        return x, y, w, h, gx, gy, maparea

    @stop_watch
    def StartDetectingMini4WD(self):
        '''
        USBカメラが使用可能でかつフラグがTrueのときミニ四駆の検知を始める.
        multiprocessingなどの並行処理で呼び出すことで，Restartさせることが
        可能．
        '''
        print('StartDetectingMini4WDが呼ばれました')
        #プロパティの宣言-----------------------------#
        gx_pre , gy_pre                         = 0,0
        self.StartFlag                          = True
        mapX_pre,mapY_pre                       = 0,0
        count                                   = self.USBCamera.get(cv2.CAP_PROP_FRAME_COUNT)
        #--------------------------------------------#

        while(self.USBCamera.isOpened() & self.StartFlag):
            ret, frame  = self.USBCamera.read()                                 # VideoCaptureから1フレーム読み込む
            
            if ret :
                self.VideoFrame      = self.M4DIP.ImagePreprocessing(frame)     # ここでビデオフレームの前処理を行う
                x,y,w,h,gx,gy,area   = \
                    self.DetectMini4WD(self.BackGroundImage,self.VideoFrame,gx_pre,gy_pre)# ミニ四駆の検知
                
                if gx == -1:                                                    # もし見つからなかったら
                    continue                                                    # 次のループへ
                
                mapX=int(gx//(self.VideoFrame.shape[1]//self.DivMapW))
                mapY=int(gy//(self.VideoFrame.shape[0]//self.DivMapH))
                self.SetInformationsOfDetection(mapX,mapY,gx,gy,w,h,area)
                if mapX!=mapX_pre or mapY!=mapY_pre:
                    self.M4DH.LocationChangeEventListner(mapX,mapY)
                    mapX_pre=mapX
                    mapY_pre=mapY
                gx_pre,gy_pre   = gx,gy                                         # 次の呼び出しのために値渡し

            if self.frameNum>=count:
                return
        cv2.destroyAllWindows()
        return

def main():
    # print('これからpythonで1375枚のフレームを処理した際の速度を示します')
    M4DIr= Mini4WDInitializer('./.settingTest')  # 初期設定を呼び出す者
    M4DH = Mini4WDHandlerForTest(M4DIr)                 # Mini4WDを制御する者
    # M4DD = Mini4WDDetectorForTest(M4DIr,M4DH)         # Mini4WDを発見する者
    # M4DD.StartDetectingMini4WD()
    print('これからcythonで1375枚のフレームを処理した際の速度を示します')
    cM4D = cMini4WDDetector(M4DIr,M4DH)
    cM4D.StartDetectingMini4WD()

if __name__ == "__main__":
    main()