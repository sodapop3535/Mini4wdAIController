import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

class Mini4WDImageProcessor():
    '''
    ここではMini4WDおよびMini4WDDetectorで用いる画像をよりオブジェクト指向っぽく
    するため（？）にクラスライブラリを実装する．
    変数の命名規則はアッパーキャメルケースでかいた．

    Attributes
    ----------
    TrimTop:int
        トリミングする上部のピクセルの数
    TrimBottom:int
        トリミングする下部のピクセルの数
    TrimRight:int
        トリミングする右側のピクセルの数
    TrimLeft:int
        トリミングする左側のピクセルの数
    '''

    def __init__(self, Mini4WDInitializer,Mini4WDHandler):
        '''
        Parameters
        ----------
        isFrame:boolean
            Frameがimage型かstring型(パス)かを示す．
            True:Frameはimage型
            False:Frameはstring型(パス) 
        Frame:image or string
            画像を読み込むもしくはパスから読み込む
        DivFrame:int
            画像の解像度．高ければ高いほど荒くなる
        '''
        self.M4DIr          = Mini4WDInitializer
        self.M4DH           = Mini4WDHandler
        self.TrimTop        = int(self.M4DIr.GetFileValue('TrimTop'))
        self.TrimBottom     = int(self.M4DIr.GetFileValue('TrimBottom'))
        self.TrimRight      = int(self.M4DIr.GetFileValue('TrimRight'))
        self.TrimLeft       = int(self.M4DIr.GetFileValue('TrimLeft'))
        self.DivFrame       = int(self.M4DIr.GetFileValue('DivFrame'))

    def GetDivFrameNum(self):
        '''
        Returns
        -------
        DivFrame:int
            解像度のレベルを返す．大きければ大きいほど荒い
        '''
        return self.DivFrame
    
    def GetTrimPixcel(self):
        '''
        Returns
        -------
        TrimTop:int
            上に何ピクセルトリミングしたのかを示す
        TrimBottom:int
            下に何ピクセルトリミングしたのかを示す
        TrimRight:int
            右に何ピクセルトリミングしたのかを示す
        TrimLeft:int
            左に何ピクセルトリミングしたのかを示す

        '''
        return self.TrimTop,self.TrimBottom,self.TrimRight,self.TrimLeft

    def ImagePreprocessing(self,img):
        '''
        画像の前処理を行う

        Parameters
        ----------
        img:array_like
            前処理したい画像配列

        Returns
        -------
        img:array_like
            前処理をし終わった画像配列

        '''

        img = img[self.TrimTop:self.TrimBottom, self.TrimLeft:self.TrimRight]
        img = cv2.resize(img, (img.shape[1]//self.DivFrame, img.shape[0]//self.DivFrame))
        img = cv2.GaussianBlur(img,(5,5),0)
        
        return img
