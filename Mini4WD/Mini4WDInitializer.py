import os
from Mini4WDException import NoFileExistException

class Mini4WDInitializer():

    '''

        Parameters
        ----------
        SettingDict:連想配列
            初期セッティングファイルの中身をキーとvalueで保存
        File:ファイル
            初期設定ファイルオブジェクト

    '''

    def __init__(self,SettingFilePath):
        '''
        
        Parameters
        ----------
        SettingFilePath:String
            初期セッティングファイルのパス(セッティングファイルを含む)
        
        '''
        self.SettingFilePath    = SettingFilePath
        self.SettingDict        = dict()
        self.File               = None
        self.ReadFile(self.SettingFilePath)

    def __del__(self):
        '''

        このインスタンスが捨てられるとき，辞書の値を更新する

        '''
        self.WriteFile(self.SettingFilePath)

    def GetFileValue(self,key):
        '''

        読み込んだ初期設定ファイルから作成したdict型において，
        keyによって指定したvalueを取り出す

        Parametars
        ----------
        key:string
            取り出したい初期設定の名前
        
        Returns
        -------
        value:string
            取り出した値．文字型であり，数値としては返却しない．

        Throws
        ------
        KeyError:
            指定されたキーが存在しなかった場合に投げられる

        '''
        return self.SettingDict[key]

    def ReadFile(self,SettingFilePath=''):
        '''
        
        指定されたファイルをpythonのdictとして保存する．

        Parameters
        ----------
        SettingFilePath:
        
        Throws
        ------
        IOError:
            セッティングファイルが読み込めなかったときの例外
        IndexError:
            セッティングファイルの中に'='が存在しなかったときの例外
        NoFileExistException:
            指定したファイルが存在しないときに投げられる独自例外
        Exception
            予期しない例外

        '''
        self.SettingFilePath=SettingFilePath
        if os.path.exists(self.SettingFilePath):
            self.File = open(SettingFilePath,'rt',encoding='UTF-8')
            for i in self.File.readlines():
                temp=i.split('=')
                self.SettingDict[temp[0].replace(' ','')]=temp[1].replace('\n','').replace(' ','')
            self.File.close()
        else:
            raise NoFileExistException

    def SetFileValue(self,key,value):
        '''
        指定されたキー値の値を更新する．もしくは新しくkeyとvalueの組み合わせを作る

        Parameters
        ----------
        key:object
            指定するキー値
        value:object
            代入する値
        '''
        self.SettingDict[key]=value

    def WriteFile(self,SettingFilePath='./.setting'):
        '''
        現在のdictの値をsettingファイルに書き込む

        Parameters
        ----------
        SettingFilePath:string default='./.setting'
            設定を保存したいファイル名

        Throws
        ------
        IOError:
            セッティングファイルが読み込めなかったときの例外
        IndexError:
            セッティングファイルの中に'='が存在しなかったときの例外
        NoFileExistException:
            指定したファイルが存在しないときに投げられる独自例外

        '''
        self.File = open(SettingFilePath,'wt',encoding='UTF-8')
        # print(self.SettingDict)
        for i in self.SettingDict.keys():
                self.File.write(str(i)+'='+str(self.SettingDict[i])+'\n')    
        self.File.close()
            