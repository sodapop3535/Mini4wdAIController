class DutyRatioException(Exception):
    '''

    Duty比が1より大きいもしくは-1より小さいなどして
    duty比として指定できない値が指定された時に
    挙げられる独自例外

    '''
    def __init__(self):
        self.main()
    def main(self):
        return 'Duty Ratio is over 1 or under -1. Please revise it.'

class NoPortOpendeException(Exception):
    '''

    指定されたポートがすでにどこかに使われていた場合に挙げられる例外

    '''
    def __init__(self):
        self.main()
    def main(self):
        return ' Any port can be used. Please retry again!'

class NoFileExistException(Exception):
    '''

    指定したセッティングファイルが存在しなかった場合にも例外を投げたいため
    独自に作成した．多分探せば標準で例外を投げてくれるようにopenやらなんやら
    を設定できるんだろうけど，独自例外作る方が早かった．
    
    '''
    def __init__(self):
        self.main()

    def main(self):
        return 'The specified File does not exist'

class InvalidOperation(Exception):
    '''

    ミニ四駆操作システムにおいて無効な操作が発生した場合に
    挙げられる例外．
    
    '''
    def __init__(self):
        self.main()

    def main(self):
        return 'What you want to operate is invalid.'

class InvalidImageFile(Exception):
    '''

    ミニ四駆操作システムにおいて選択した背景画像が不正だった時に
    投げられる例外
    
    '''
    def __init__(self):
        self.main()

    def main(self):
        return 'Either Image File Path or Image File Type that you want to open is invalid.'

class InvalidDutyMap(Exception):
    '''

    ミニ四駆操作システムにおいてインポートしたdutymapであるcsvファイルが不正
    な構成になっていた場合に投げられる例外
    
    '''
    def __init__(self):
        self.main()

    def main(self):
        return 'It is invalid that the csv file which you choose.'

class NotAllowedValue(Exception):
    '''

    このシステムにおいて不当な数値が割り当てられたときに挙げられる例外．
    
    '''
    def __init__(self):
        self.main()

    def main(self):
        return 'This value is forbidded in this system.'

class CameraIsNotOpened(Exception):
    '''

    カメラが開いていなかったときの処理
    
    '''
    def __init__(self):
        self.main()

    def main(self):
        return 'Camera which you want to use is not opened!'

class FailedCapturingBGSI(Exception):
    '''

    背景画像の取得に失敗したときのクラス
    
    '''
    def __init__(self):
        self.main()

    def main(self):
        return 'I am sorry. This program failed capturing back ground substractor.'
