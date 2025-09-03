#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 12/08/2018

# Version 1.0
#=======================================================================================================================
import random
# 引入隨機數模塊

class Camera:
    """相機機身"""

    # 對焦類型
    SingleFocus = "單點對焦"
    AreaFocus = "區域對焦"
    BigAreaFocus = "大區域對焦"
    Focus45 = "45點自動對焦"

    def __init__(self, name):
        self.__name = name
        self.__aperture = 0.0       # 光圈
        self.__shutterSpeed = 0     # 快門速度
        self.__ligthSensitivity = 0 # 感光度
        self.__lens = Lens()        # 鏡頭
        self.__sdCard = SDCard()    # SD卡
        self.__display = Display()  # 顯示器

    def shooting(self):
        """拍照"""
        print("[開始拍攝中")
        imageLighting = self.__lens.collecting()
        # 通過快門、光圈和感光度、測光來控制拍攝的過程，省略此部分
        image = self.__transferImage(imageLighting)
        self.__sdCard.addImage(image)
        print("拍攝完成]")

    def viewImage(self, index):
        """查看圖像"""
        print("查看第%d張圖像：" % (index + 1))
        image = self.__sdCard.getImage(index)
        self.__display.showImage(image)

    def __transferImage(self, imageLighting):
        """接收光線並處理成數字信號，簡單模擬"""
        print("接收光線並處理成數字信號")
        return Image(6000, 4000, imageLighting)

    def setting(self, aperture, shutterSpeed, ligthSensitivity):
        """設置相機的拍攝屬性：光圈、快門、感光度"""
        self.__aperture = aperture
        self.__shutterSpeed = shutterSpeed
        self.__ligthSensitivity = ligthSensitivity

    def focusing(self, focusMode):
        """對焦，要通過鏡頭來調節焦點"""
        self.__lens.setFocus(focusMode)

    def showInfo(self):
        """顯示相機的屬性"""
        print("%s的設置   光圈：F%0.1f  快門：1/%d  感光度：ISO %d" %
              (self.__name, self.__aperture, self.__shutterSpeed, self.__ligthSensitivity))


class Lens:
    """鏡頭"""

    def __init__(self):
        self.__focusMode = ''   # 對焦
        self.__scenes = {0 : '風光', 1 : '生態', 2 : '人文', 3 : '紀實', 4 : '人像', 5 : '建築'}

    def setFocus(self, focusMode):
        self.__focusMode = focusMode

    def collecting(self):
        """圖像採集，採用隨機的方式來模擬自然的拍攝過程"""
        print("採集光線，%s" % self.__focusMode)
        index = random.randint(0, len(self.__scenes)-1)
        scens = self.__scenes[index]
        return "美麗的 " + scens + " 圖像"


class Display:
    """顯示器"""

    def showImage(self, image):
        print("圖片大小：%d x %d，  圖片內容：%s" % (image.getWidth(), image.getHeight(), image.getPix()))


class SDCard:
    """SD存儲卡"""

    def __init__(self):
        self.__images = []

    def addImage(self, image):
        print("存儲圖像")
        self.__images.append(image)

    def getImage(self, index):
        if (index >= 0 and index < len(self.__images)):
            return self.__images[index]
        else:
            return None


class Image:
    """圖像(圖片), 方便起見用字符串來代碼圖像的內容(像素)"""

    def __init__(self, width, height, pixels):
        self.__width = width
        self.__height = height
        self.__pixels = pixels

    def getWidth(self):
        return  self.__width

    def getHeight(self):
        return self.__height

    def getPix(self):
        return self.__pixels


# Version 2.0
#=======================================================================================================================
# 代碼框架
#==============================

# 基於框架的實現
#==============================


# Test
#=======================================================================================================================
def testCamera():
    camera = Camera("EOS 80D")
    camera.setting(3.5, 60, 200)
    camera.showInfo()
    camera.focusing(Camera.BigAreaFocus)
    camera.shooting()
    print()

    camera.setting(5.6, 720, 100)
    camera.showInfo()
    camera.focusing(Camera.Focus45)
    camera.shooting()
    print()

    camera.viewImage(0)
    camera.viewImage(1)


testCamera()