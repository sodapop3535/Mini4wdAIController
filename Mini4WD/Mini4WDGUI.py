import wx
import os
import threading
import time
import cv2

class Mini4WDGUI(wx.Frame):
    def __init__(self,*args, **kw):
        super(Mini4WDGUI, self).__init__(*args, **kw)
        self.DetectionButtonID1 = self.NewControlId()
        self.DetectionButtonID2 = self.NewControlId()
        self.Mini4WDButtonID1   = self.NewControlId()
        self.Mini4WDButtonID2   = self.NewControlId()
        self.CameraButtonID     = self.NewControlId()
        self.CameraFlag         = True
        self.M4DIr              = None
        self.M4DH               = None
        self.M4DD               = None
        self.count              = 0

    def ini_frame(self,M4DD):
        '''
        フレームの基本的なレイアウトを作成する
        '''
        self.M4DD       = M4DD
        self.M4DIr      = self.M4DD.GetM4DIr()
        self.M4DH       = self.M4DD.GetM4DH()
        self.M4DL       = self.M4DD.GetM4DL()
        self.M4DM       = self.M4DH.GetM4DM()
        self.write_ini_log()
        
        # get bitmap image
        self.image = self.AdjustImage(wx.Image(self.M4DD.GetBGSIPath()))
        
        # set frame's fundamental parameters
        self.SetTitle('Mini4WD Controller')
        self.SetWindowStyle(style= wx.RESIZE_BORDER | wx.MINIMIZE_BOX  | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.Refresh()
        self.SetIcon(wx.Icon(wx.Bitmap('./img/icon/Mini4WD.ico')))

        self.dp = DutyPanel(self, self.M4DH, self.image)

        # initialize Sizer
        self.bsV=wx.BoxSizer(wx.VERTICAL)
        bsH1 = wx.BoxSizer(wx.HORIZONTAL)

        # Adding the MenuBar to the Frame content.
        self.SetMenuBar(self.CreateMenubar())

        # make the first line that is in this frame
        bsH1.Add(self.dp.GetPanel1(),proportion=2,flag=wx.EXPAND|wx.ALL,border=10)
        bsH1.Add(self.dp.GetPanel2(),proportion=1,flag=wx.EXPAND|wx.ALL,border=10)

        # add lines to verticl boxsizer
        self.bsV.Add(bsH1,proportion=0,flag=wx.EXPAND|wx.ALL,border=10)

        # add toolbar
        self.toolbar = self.Toolbar()

        self.SetSize((self.image.GetWidth()+150, self.image.GetHeight()+self.toolbar.GetSize()[1]+200))
        self.Move((0,0))
        self.SetBackgroundColour(wx.Colour(0,0,0))
        
        self.SetToolBar(self.toolbar)

        # set toolbar text
        pos  = self.toolbar.GetPosition().Get()
        txt1 = wx.StaticText(self,label="MINI4WD DETECTION",pos=(pos[0]+95,pos[1]-45))
        txt2 = wx.StaticText(self,label="MINI4WD",pos=(pos[0]+385,pos[1]-45))
        txt3 = wx.StaticText(self,label="CAMERA",pos=(pos[0]+590,pos[1]-45))

        txt1.SetForegroundColour(wx.Colour('white'))
        txt2.SetForegroundColour(wx.Colour('white'))
        txt3.SetForegroundColour(wx.Colour('white'))

        # A Statusbar in the bottom of the window
        self.CreateStatusBar()

        # apply sizer with this frame
        self.SetSizer(self.bsV)

        # Show this Frame
        self.Show()

    def AdjustImage(self,image):
        '''
        渡された画像をいいように加工する

        Parameters
        ----------
        image:wx.Image
            変更したい画像
        width:int
            変更後の画像サイズ

        Returns
        -------
        image:wx.Image
            変更後の画像

        '''

        # 画面に映す画像の幅に関する制限を設定
        width = 550
        height = int(width*0.75)

        # その設定に合わせて画像を拡大または縮小
        w,h = image.GetWidth(), image.GetHeight()

        if w >= h:
            ratio = width / w
            image.Rescale(width,int(h*ratio))
        if w < h:
            ratio = height / h
            image.Rescale(int(w*ratio),height)

        return image

    def Toolbar(self):
        '''
        下のツールバーを作成する
        '''
        toolbar = wx.ToolBar(self,style=wx.TB_BOTTOM)
        toolbar.SetBackgroundColour(wx.Colour(0,0,0))
        # toolbar.SetForegroundColour((255,0,0))
        font = wx.Font((10,30),wx.DEFAULT,style=wx.NORMAL,weight=wx.NORMAL)
        toolbar.SetFont(font)

        toolbar.AddSeparator()
        # DetectionButton = toolbar.AddTool(self.DetectionButtonID, label="test", bitmap=wx.Bitmap('./img/button/button_start.ico')\
        #     ,bmpDisabled=wx.Bitmap('./img/button/button_stop.ico'))
        DetectionButton1 = toolbar.AddTool(self.DetectionButtonID1, label="test", bitmap=wx.Bitmap('./img/button/button_start.ico'))
        DetectionButton2 = toolbar.AddTool(self.DetectionButtonID2, label="test", bitmap=wx.Bitmap('./img/button/button_stop.ico'))
        toolbar.EnableTool(self.DetectionButtonID2, False)

        toolbar.AddSeparator()
        # Mini4WDButton = toolbar.AddTool(self.Mini4WDButtonID, label="test", bitmap=wx.Bitmap('./img/button/button_run.ico')\
        #     ,bmpDisabled=wx.Bitmap('./img/button/button_stop2.ico'))
        Mini4WDButton1 = toolbar.AddTool(self.Mini4WDButtonID1, label="test", bitmap=wx.Bitmap('./img/button/button_run.ico'))
        Mini4WDButton2 = toolbar.AddTool(self.Mini4WDButtonID2, label="test", bitmap=wx.Bitmap('./img/button/button_stop2.ico'))
        toolbar.EnableTool(self.Mini4WDButtonID2, False)

        toolbar.AddSeparator()
        
        CameraButton = toolbar.AddTool(self.CameraButtonID, label="test", bitmap=wx.Bitmap('./img/button/button_show.ico'))

        # イベントハンドラーの追加
        toolbar.Bind(wx.EVT_TOOL, self.OnDetection, DetectionButton1)
        toolbar.Bind(wx.EVT_TOOL, self.OffDetection, DetectionButton2)
        toolbar.Bind(wx.EVT_TOOL, self.OnMini4WD, Mini4WDButton1)
        toolbar.Bind(wx.EVT_TOOL, self.OffMini4WD, Mini4WDButton2)
        toolbar.Bind(wx.EVT_TOOL, self.OnCamera, CameraButton)

        toolbar.Realize()

        return toolbar

    def CreateMenubar(self):
        '''
        上のメニューバーを作成する
        '''
        # Setting up the menu.
        filemenu= wx.Menu()
        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        menuItem1=filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        # Open Menuの追加
        openmenu = wx.Menu()
        omenuItem1 = openmenu.Append(wx.ID_ANY,"&back ground substractor image")
        omenuItem2 = openmenu.Append(wx.ID_ANY,"&Duty Map")
        menuItem2 = filemenu.Append(wx.ID_OPEN,"&Open",openmenu)
        # Save Menuの追加
        savemenu = wx.Menu()
        smenuItem1 = savemenu.Append(wx.ID_ANY,"&back ground substractor image")
        smenuItem2 = savemenu.Append(wx.ID_ANY,"&Duty Map")
        menuItem3=filemenu.Append(wx.ID_SAVEAS,"&Save as...",savemenu)
        # 区切り線の追加
        filemenu.AppendSeparator()
        # Exitの追加
        menuItem4=filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        # associate menuItems with functions
        self.Bind(wx.EVT_MENU, self.OnAbout, menuItem1)
        self.Bind(wx.EVT_MENU, self.OnOpenImage, omenuItem1)
        self.Bind(wx.EVT_MENU, self.OnOpenDutyMap, omenuItem2)
        self.Bind(wx.EVT_MENU, self.OnSaveImage, smenuItem1)
        self.Bind(wx.EVT_MENU, self.OnSaveDutyMap, smenuItem2)
        self.Bind(wx.EVT_MENU, self.OnExit, menuItem4)

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        return menuBar

    def OnDetection(self,e):
        '''
        ミニ四駆検知と操作を終了する．
        '''
        toolbar = e.GetEventObject()
        toolbar.EnableTool(self.DetectionButtonID1, False)
        toolbar.EnableTool(self.DetectionButtonID2, True)
        toolbar.EnableTool(self.Mini4WDButtonID1, False)
        toolbar.EnableTool(self.Mini4WDButtonID2, False)
        toolbar.EnableTool(self.CameraButtonID, False)
        self.M4DL.UpdateDetectionLogFile()
        self.M4DL.WriteOperationLog('Detection is started , file number is {} and Epoch Time is {}'.format(self.M4DL.GetDetectionLogFileNum(),time.time()))
        detectThread = threading.Thread(target=self.M4DD.StartDetectingMini4WD)
        detectThread.start()

    def OffDetection(self,e):
        '''
        ミニ四駆検知と操作を終了する．
        '''
        toolbar = e.GetEventObject()
        toolbar.EnableTool(self.DetectionButtonID1, True)
        toolbar.EnableTool(self.DetectionButtonID2, False)
        toolbar.EnableTool(self.Mini4WDButtonID2, True)
        toolbar.EnableTool(self.CameraButtonID, True)
        self.M4DD.StopDetectingMini4WD()
        self.M4DH.SendDutyCommand(0)
        self.M4DH.currentDutyRatio = 0
        self.M4DL.WriteOperationLog('Detection is stopped.')

    def OnMini4WD(self,e):
        '''
        ミニ四駆検知関係なくミニ四駆を走らせるときに使う
        '''
        toolbar = e.GetEventObject()
        toolbar.EnableTool(self.Mini4WDButtonID1, False)
        toolbar.EnableTool(self.Mini4WDButtonID2, True)
        self.M4DH.SendDutyCommand(1)
        self.M4DL.WriteOperationLog('On Mini4WD Button pressed and Epoch Time is {}'.format(time.time()))

    def OffMini4WD(self,e):
        '''
        ミニ四駆を止めるときに使う
        '''
        toolbar = e.GetEventObject()
        toolbar.EnableTool(self.Mini4WDButtonID1, True)
        toolbar.EnableTool(self.Mini4WDButtonID2, False)
        self.M4DH.SendDutyCommand(0)
        self.M4DL.WriteOperationLog('Off Mini4WD Button pressed and Epoch Time is {}'.format(time.time()))
        self.M4DH.currentDutyRatio = 0

    def OnCamera(self,e):

        if self.count%2 ==0:
            self.M4DD.ShowFrame()
        else:
            self.M4DD.CloseFrame()
        self.count +=1

    def OnAbout(self,event):
        '''
        メニューバーのAboutが押された時の処理
        '''
        # if event==wx.EVT_MENU:
        #     print(0)

        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "A small text editor", "About Sample Editor", wx.OK)
        # or you can write under program instead of above programe
        # dlg = wx.MessageDialog( self, "A small text editor", "About Sample Editor")
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,event):
        self.Close(True)

    def OnPaint(self,event):
        panel = event.GetEventObject()
        dc = wx.ClientDC(panel)
        dc.SetPen(wx.Pen("red",width=10))
        x, y = panel.GetSize()
        dc.DrawLine(0, 0, x, y)

    def OnOpenImage(self,event):
        '''
        メニュー画面より，背景画像を開く．
        '''
        self.dirname = ''
        with wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN) as dlg:
            dlg.SetDirectory('./img/')
            if dlg.ShowModal() == wx.ID_OK:
                try:
                    self.M4DD.SetBGSI(dlg.GetPath())
                except Exception as e:
                    md = wx.MessageDialog(self,e.main(),'Error',wx.OK)
                    md.ShowModal()  # Show it
                    md.Destroy()    # finally destroy it when finished.

    def OnOpenDutyMap(self,event):
        '''
        メニューバーより，duty mapを保存したcsvファイルを開き，現在のduty mapに適用する．
        '''
        self.dirname = ''
        with wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN) as dlg:
            dlg.SetDirectory('./dmap/')
            if dlg.ShowModal() == wx.ID_OK:
                try:
                    self.bsV.Clear(True)
                    
                    self.M4DM.ApplyCSVFileWithDmap(dlg.GetPath())
                    self.dp = DutyPanel(self,self.M4DH,self.image)
                    bsH1=wx.BoxSizer(wx.HORIZONTAL)
                    # # make the first line that is in this frame
                    bsH1.Add(self.dp.GetPanel1(),proportion=2,flag=wx.EXPAND|wx.ALL,border=10)
                    bsH1.Add(self.dp.GetPanel2(),proportion=1,flag=wx.EXPAND|wx.ALL,border=10)
                    
                    self.bsV.Add(bsH1)
                    
                    # self.Refresh(True)
                    self.SetSizerAndFit(self.bsV)
                    
                except IOError as e:
                    md = wx.MessageDialog(self,'ファイルが開けません','Error',wx.OK)
                except Exception as e:
                    md = wx.MessageDialog(self,e.main(),'Error',wx.OK)
                    md.ShowModal()  # Show it
                    md.Destroy()    # finally destroy it when finished.

    def OnSaveImage(self,event):
        '''
        フレーム上部でSave as ... において，back ground substractor image
        を選択した際の処理．現在システムが持っている背景画像を保存する．
        '''
        with wx.FileDialog(self, "Save back ground substractor image", wildcard="png (*.png)|*.png|jpg (*.jpg)|*.jpg",
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            fileDialog.SetDirectory('./img/')
            fileDialog.SetFilename(time.strftime("%Y%m%d%H%M%S", time.gmtime()))

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                self.M4DD.SaveBackGroundSubstractorImage(pathname)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    def OnSaveDutyMap(self,event):
        '''
        フレーム上部のSave as ...でduty mapを選択した際の処理．
        現在表示しているdutymapをcsv形式で保存する．
        '''
        with wx.FileDialog(self, "Save duty map as csv file", wildcard="csv (*.csv)|*.csv",
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            fileDialog.SetDirectory('./dmap/')
            fileDialog.SetFilename(time.strftime("%Y%m%d%H%M%S", time.gmtime()))

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                self.M4DM.SaveDutyMapAsCSV(pathname)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    def GetM4DD(self):
        return self.M4DD

    def write_ini_log(self):
        self.M4DL.WriteOperationLog('Mini4WD Conntroller is started .')
        
        self.M4DL.WriteOperationLog('\
            ---Mini4WD Handler Information---\n\
            Div Map H:{}\n\
            Div Map W:{}'.format(self.M4DH.GetDivMapH(),self.M4DH.GetDivMapW()))

        self.M4DL.WriteOperationLog('\
            ---Mini4WD Duty Map Information---\n\
            Duty Map:\n\
            \t{}\
        '.format(self.M4DM.GetDutyMap()))

        self.M4DL.WriteOperationLog('\
            ---Mini4WD Image Processing Information---\n\
            Div Frame Num:{}\n\
            Trim Pixcel:{}(top,bottom,left,right)\
        '.format(self.M4DD.GetM4DIP().GetDivFrameNum(),self.M4DD.GetM4DIP().GetTrimPixcel()))

        self.M4DL.WriteOperationLog('\
            ---Mini4WD Detector Information---\n\
            Mini4WD Max Size:{}\n\
            Mini4WD Min Size:{}\n\
            Back Ground Substractor Image Path:{}\
        '.format(self.M4DD.GetMini4WDMaxSize(),self.M4DD.GetMini4WDMinSize(),self.M4DD.GetBGSIPath()))

class DutyPanel():
    '''

    Parameters
    ----------
    dh:int
        画像を指定された数だけ分割したときの縦幅
    dw:int
        画像を指定された数だけ分割したときの横幅
    dutyMapImage:list context=wx.Image
        画像を分割したものをその順番に配列に保存したもの
    dutyMapImageWithText:list context=wx.Bitmap
        その場所に該当するduty比を記載した分割画像
    p1:wx.Panel
        分割した画像をボタンとして表示しているパネル
    p2:wx.Panel
        スライドウィジェットを表示しているパネル
    '''
    def __init__(self,parent,M4DH,image):
        '''
        Parameters
        ----------
        parent:wx.Frame
            これを呼び出した親フレーム
        image:wx.Image
            今回選択した背景画像
        divmapH:int
            エリアの縦の分割数
        divmapW:int
            エリアの横の分割数
        '''
        self.parent = parent
        self.M4DH = M4DH
        self.M4DM = self.M4DH.GetM4DM()
        self.dh = -1
        self.dw = -1
        self.dutyMapImage, self.dutyMapImageWithText = self.DevideImage(self.M4DM.GetDutyMap(),image)
        self.p1 = Panel1(parent)
        self.p1.ini_pannel(self,self.dutyMapImageWithText,self.dh,self.dw)
        self.p2 = Panel2(parent)
        self.p2.ini_panel(self)
        self.SetP2Disable()

    def AdjustImage(self,image):
        '''
        渡された画像をいいように変換する
        '''
        width = self.parent.GetSize()[0]-175
        ratio = width / image.GetWidth()
        image.Rescale(width,int(image.GetHeight()*ratio))
        
        # print('width:{},height:{},ratio:{}'.format(width,int(image.GetHeight()*ratio),ratio))
        return image

    def SetP2Enable(self):
        '''
        ボタンが選択されたときにスライドを使える
        ようにしておく処理
        '''
        self.p2.Enable()
    
    def SetP2Disable(self):
        '''
        ボタンが選択されていないときにスライドを使えない
        ようにしておく処理
        '''
        self.p2.Disable()

    def ReflectButtonSelectionToP2Slider(self,x,y):
        '''
        画像（ボタン）を選択したときに選んだエリアのduty比をスライドに
        反映させる.

        Parameters
        ----------
        x:int
            選択したエリアの横の番号
        y:int
            選択したエリアの縦の番号
        '''
        txt = self.p2.GetdutyLabel()
        sld = self.p2.GetSlider()
        dutyValue = self.M4DM.GetDutyRatio(x,y)
        sld.SetValue(dutyValue*100)
        txt.SetLabel(str(int(dutyValue*100+0.1))+'%')

    def GetPanel1(self):
        '''
        画像を表示している領域（パネル）のインスタンスを返す．

        Returns
        -------
        p1:wx.Panel
            パネルオブジェクト
        '''
        return self.p1
    
    def GetPanel2(self):
        '''
        つまみを表示している領域（パネル）のインスタンスを返す．

        Returns
        -------
        p2:wx.Panel
            パネルオブジェクト
        '''
        return self.p2

    def DevideImage(self,dutyMap,image):
        '''
        引数の画像をdutyMapをもとに分割し，dutyMapImageとdutyMapImageWithText
        を作成する

        Parameters
        ----------
        dutyMap:list context=int
            duty比が格納されたリスト型配列
        image:wx.Image
            分割する画像

        Returns
        -------
        dutyMapImage:list context=wx.Image
            ただ分割した画像が配列としておさまっている
        dutyMapImageWithText :list context=wx.Bitmap
            分割し，そこに該当するduty比がおさまっている

        '''
        # 分割数の取得
        divmapH                 = len(dutyMap)
        divmapW                 = len(dutyMap[0])
        # 分割後の画像一つ当たりの縦と横の長さ
        self.dh                 = int(image.GetHeight()/divmapH)
        self.dw                 = int(image.GetWidth()/divmapW)
        # initialize
        dutyMapImage            = list()
        dutyMapImageWithText    = list()
        
        # 分割数だけ画像を分割し，dutyMapImageとdutyMapImageWithTextを作成する
        for i in range(divmapH):
            temp1 = list()
            temp2 = list()
            for j in range(divmapW):
                img     = image.Copy()
                img     = img.GetSubImage(wx.Rect((self.dw*j, self.dh*i), (self.dw, self.dh)))
                bitmap1 = img
                bitmap2 = img.ConvertToBitmap()
                temp1.append(bitmap1)
                temp2.append(self.WriteDutyMapImageWithText(dutyMap[i][j],bitmap2))
            dutyMapImage.append(temp1)
            dutyMapImageWithText.append(temp2)
        return dutyMapImage, dutyMapImageWithText

    def WriteDutyMapImageWithText(self,duty,bitmap):
        '''
        指定されたduty比をビットマップ画像に書き込む

        Parameters
        ----------
        duty:int
            duty比
        bitmap:wx.Bitmap
            ビットマップ画像
        '''
        mdc=wx.MemoryDC(bitmap)
        mdc.SetFont(wx.Font((int(self.dw/10),int(self.dh/2)), wx.DECORATIVE, wx.SLANT, wx.NORMAL))
        mdc.SetTextForeground((255,125,0))
        mdc.DrawText(str(int(duty*100+0.1))+'%',self.dw/2-3,self.dh/2-3)
        return bitmap

    def UpdateDutyMap(self, duty):
        '''
        Panel2のスライダーが変更された時にその値に合わせてボタンを変更する

        Parameters
        ----------
        duty:int
            変更後のduty比
        '''
        bt = self.p1.GetFocusedButton()                         # 現在選択されているボタンの取得
        y, x = bt.h, bt.w                                       # そのボタンのエリアの取得

        # もしミニ四駆の現在地点のduty比を変えたのならそれを反映する
        temp_x, temp_y = self.parent.GetM4DD().GetMini4WDLocation()
        if temp_x == x and temp_y == y and self.parent.GetM4DD().StartFlag == True:
            self.M4DH.SendDutyRatio(duty/100)

        self.M4DM.SetDutyRatio(x, y, duty/100)                  # duty比をパーセントから比率に変える
        self.dutyMapImageWithText[y][x]=\
            self.WriteDutyMapImageWithText(duty/100, self.dutyMapImage[y][x].ConvertToBitmap())
        bt.SetBitmap(self.dutyMapImageWithText[y][x])           # bitmapの更新

class Panel1(wx.Panel):
    '''
    dp:DutyPanel
        duty比に関する処理を手掛けるクラスのインスタンスであり，呼び出し元
    dh:int
        分割した画像の一枚当たりの縦の長さ
    dw:int
        分割した画像の一枚当たりの横の長さ
    focusColor:wx.Colour
        ボタンが選ばれているときの背景色
    backColor:wx.Color
        このパネルの背景色
    focusedButton:wx.BitmapButton
        選択されているボタン
    '''
    def __init__(self,*args,**kw):
        super(Panel1,self).__init__(*args,**kw)
        self.dp=None
        self.dh=-1
        self.dw=-1
        self.focusColor=wx.Colour(255,125,0)
        self.backColor=wx.Colour(120,120,120)
        self.focusedButton = None
        self.gridBorder = 2

    def ini_pannel(self,dp,dutyMapImageWithText,dh,dw):
        '''
        このパネルのレイアウトの作成

        Parameters
        ----------
        dp:DutyPanel
            duty比に関する処理を手掛けるクラスのインスタンスであり，呼び出し元
        dutyMapImageWithText:list context=wx.Bitmap
            duty比が記載されたビットマップ画像
        dh:int
            分割した画像の一枚当たりの縦の長さ
        dw:int
            分割した画像の一枚当たりの横の長さ

        '''
        self.dp             = dp
        self.dh,self.dw     = dh,dw
        divmapH             = len(dutyMapImageWithText)
        divmapW             = len(dutyMapImageWithText[0])

        # create and set color
        self.SetBackgroundColour(self.backColor)
        bsV=wx.BoxSizer(wx.VERTICAL)
        self.txt = wx.StaticText(self, label="Power Map",style=wx.ST_NO_AUTORESIZE)

        # define grid sizer
        gs = wx.GridSizer(divmapH,divmapW,0,0)

        for i in range(divmapH):
            for j in range(divmapW):
                bt      = wx.BitmapButton(self, wx.ID_ANY, bitmap=dutyMapImageWithText[i][j],size=(self.dw,self.dh))
                bt.w    = j
                bt.h    = i
                gs.Add(bt,flag=wx.ALL,border=self.gridBorder)
                self.Bind(wx.EVT_BUTTON,self.OnButtonClick,bt)

        # self.Bind(wx.EVT_PAINT,self.OnPaint,self)
        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus,self)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus,self)

        bsV.Add(self.txt, flag=wx.ALIGN_CENTER)
        bsV.Add(gs,flag = wx.ALIGN_CENTER)

        self.SetSizer(bsV)

    def OnButtonClick(self, event):
        '''
        ボタンが押された時の処理
        '''
        bt = event.GetEventObject()
        self.focusedButton = bt
        self.dp.SetP2Enable()
        self.dp.ReflectButtonSelectionToP2Slider(bt.w,bt.h)
        ############ drawing focus process#############
        cdc=wx.ClientDC(self)
        cdc.SetBrush(wx.Brush(self.backColor))
        cdc.Clear()
        cdc.SetPen(wx.Pen(self.focusColor))
        cdc.SetBrush(wx.Brush(self.focusColor))
        w, h = bt.GetSize()
        x, y = bt.GetPosition()
        cdc.DrawRectangle(wx.Rect(x-self.gridBorder,y-self.gridBorder,w+self.gridBorder*2,h+self.gridBorder*2))

    def OnSetFocus(self,e):
        self.focusedButton=None
        cdc=wx.ClientDC(self)
        cdc.SetBrush(wx.Brush(self.backColor))
        cdc.Clear()

    def OnKillFocus(self,e):
        self.focusedButton=None
        cdc=wx.ClientDC(self)
        cdc.SetBrush(wx.Brush(self.backColor))
        cdc.Clear()

    def GetFocusedButton(self):
        '''
        現在選択されているボタンを返却する
        '''
        return self.focusedButton

class Panel2(wx.Panel):
    '''
    Parameters
    ----------
    backColor:wx.Colour
        背景の色を扱うオブジェクト
    sld:wx.Slider
        duty比を変更するためのつまみ
    '''

    def __init__(self,*args, **kw):
        super(Panel2,self).__init__(*args, **kw)
        self.dp         = None
        self.backColor  = wx.Colour(120,120,120)
        self.sld        = None

    def ini_panel(self, dp):
        '''
        このパネルのレイアウトの作成

        Parameters
        ----------
        dp:DutyPanel
            duty比に関する処理を手掛けるクラスのインスタンスであり，呼び出し元
        M4DH:Mini4WDHandler

        '''
        self.dp     = dp
        self.SetBackgroundColour(self.backColor)
        bsV         = wx.BoxSizer(wx.VERTICAL)
        txt1        = wx.StaticText(self, label="Mini4WD Power",\
            style=wx.ALIGN_CENTRE_HORIZONTAL|wx.ST_NO_AUTORESIZE)
        self.font=wx.Font((10,13),wx.DEFAULT,style=wx.NORMAL,weight=wx.NORMAL)
        self.SetFont(self.font)

        # create duty slider
        self.sld    = wx.Slider(self, value=50, minValue=0, maxValue=100,
                        style=wx.SL_VERTICAL|wx.SL_INVERSE|wx.SL_AUTOTICKS|wx.SL_MIN_MAX_LABELS|wx.SL_LEFT)
        
        self.sld.Bind(wx.EVT_SCROLL, self.OnSliderScroll)
        self.sld.Bind(wx.EVT_SCROLL_CHANGED, self.OnSliderScrollChanged)

        # stick percent text under slider
        self.font   = wx.Font((10,20),wx.DEFAULT,style=wx.NORMAL,weight=wx.NORMAL)
        self.SetFont(self.font)
        self.dutyLabel = wx.StaticText(self, label=str(self.sld.GetValue())+'%',\
            style=wx.ALIGN_CENTRE_HORIZONTAL|wx.ST_NO_AUTORESIZE)

        # add widgets in box sizer
        bsV.Add(txt1,proportion=1,flag=wx.ALIGN_CENTER|wx.EXPAND)
        bsV.Add(self.sld,proportion=8,flag=wx.ALIGN_CENTER|wx.LEFT, border=int(self.sld.GetSize()[0]/2))
        bsV.Add(self.dutyLabel,proportion=1,flag=wx.ALIGN_CENTER|wx.EXPAND)
        # apply sizer with this frame
        self.SetSizer(bsV)

    def OnSliderScroll(self, e):
        '''
        スライドをスクロールしたときの処理．
        スライドの下にある%が変化する.
        '''
        self.dutyLabel.SetLabel(str(e.GetEventObject().GetValue())+'%')
    
    def OnSliderScrollChanged(self,e):
        '''
        スライドのつまみを放したときの処理．
        放した瞬間にduty比が反映される．
        '''
        self.dutyLabel.SetLabel(str(e.GetEventObject().GetValue())+'%')
        self.dp.UpdateDutyMap(e.GetEventObject().GetValue())
        
    def GetSlider(self):
        '''
        スライドオブジェクトを返す．
        ボタンを押したときに，そのエリアのduty比をスライドへ反映させるために作った．

        Returns
        -------
        sld:wx.Slider
            スライドオブジェクト
        '''
        return self.sld

    def GetdutyLabel(self):
        '''
        スライドの下のパーセンテージを表示しているインスタンスを返す

        Returns
        -------
        dutyLabel:wx.StaticTxt?
            スタティックテキストオブジェクト
        '''
        return self.dutyLabel

if __name__=="__main__":
    main()
    