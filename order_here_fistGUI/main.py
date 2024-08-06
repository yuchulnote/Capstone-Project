import os
import sys
import tkinter as tk
import time

from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import*
from PyQt5 import uic
from PyQt5.QtTest import QTest
from secondGUI import SecondClass

from pyModbusTCP.server import ModbusServer, DataBank
from time import sleep
from popUpGUI import PopupClass

'''PyInstaller로 프로그램을 생성하였을 때, 코드에서 호출하는 파일을 상대경로로 호출하기 위한 함수입니다.'''
# @(lambda f: f())
def _(): os.chdir(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))))

form_class = uic.loadUiType("order_here.ui")[0]

# Modbus Server
# local_host = '172.100.5.64'
# local_host = '172.20.10.3'
# local_host = '172.100.14.74'
# local_host = '172.100.2.9'
local_host = '192.168.137.3' # HMM
server = ModbusServer(host=local_host, port=505, no_block=True)#, unit_id=255)
# StartTcpServer(local_host, 502)
server.start()
print('Server is online')

class WindowClass(QMainWindow, form_class):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.numAme = 0
        self.numLatte = 0
        self.numWater = 0
        self.numMilk = 0
        self.numShot = 0
        self.orderNum = 100

        self.Orderlist = [self.widget_2, self.widget_3, self.widget_4, self.widget_5, self.widget_6]
        self.Numlist = [self.num1, self.num2, self.num3, self.num4, self.num5]
        self.clickFlag = 0
        
        self.setAme = False
        self.setLatte = False
        self.setWater = False
        self.setMilk = False
        self.setShot = False

        self.AmeListNum = 0
        self.LatteListNum = 0
        self.WaterListNum = 0
        self.MilkListNum = 0
        self.ShotListNum = 0

    def initUI(self):
        self.setupUi(self)
        self.setWindowTitle('ORDER HERE')
        self.setInitStyle()
        self.show()

    def setInitStyle(self):
        self.imgAmericano.setStyleSheet("border-image: url(./images/americano.png);")
        self.imgIcelatte.setStyleSheet("border-image: url(./images/icelatte.jpg);")
        self.imgWater.setStyleSheet("border-image: url(./images/icewater.png);")
        self.imgMilk.setStyleSheet("border-image: url(./images/milk.png);")
        self.imgShot.setStyleSheet("border-image: url(./images/shot.png);")

        self.americanoButton.clicked.connect(lambda: self.clickAme())
        self.latteButton.clicked.connect(lambda: self.clickLatte())
        self.waterButton.clicked.connect(lambda: self.clickWater())
        self.milkButton.clicked.connect(lambda: self.clickMilk())
        self.shotButton.clicked.connect(lambda: self.clickShot())
        self.orderButton.clicked.connect(lambda: self.clickOrder())
        self.reset.clicked.connect(lambda: self.clickReset())


    def clickAme(self):
        #
        # print("click Americano")
        # if self.setAme == False:
        #     self.AmeListNum = self.clickFlag
        #     self.clickFlag += 1
        #     self.setAme = True

        # self.numAme += 1
        # self.Orderlist[self.AmeListNum].setStyleSheet("border-image: url(./images/americano.jpg);")
        # self.Numlist[self.AmeListNum].setText("%d 잔"%(self.numAme))
        print("click Americano")
        if self.setAme == False:
            self.AmeListNum = self.clickFlag
            self.clickFlag += 1
            self.setAme = True

        self.numAme += 1
        self.Orderlist[self.AmeListNum].setStyleSheet("border-image: url(./images/americano.png);")
        self.Numlist[self.AmeListNum].setText("%d 잔"%(self.numAme))


    def clickLatte(self):
        #
        print("click Latte")
        if self.setLatte == False:
            self.LatteListNum = self.clickFlag
            self.clickFlag += 1
            self.setLatte = True

        self.numLatte += 1
        self.Orderlist[self.LatteListNum].setStyleSheet("border-image: url(./images/icelatte.jpg);")
        self.Numlist[self.LatteListNum].setText("%d 잔"%(self.numLatte))


    def clickWater(self):
        print("click Water")
        if self.setWater == False:
            self.WaterListNum = self.clickFlag
            self.clickFlag += 1
            self.setWater = True
        self.numWater += 1
        self.Orderlist[self.WaterListNum].setStyleSheet("border-image: url(./images/icewater.png);")
        self.Numlist[self.WaterListNum].setText("%d 잔"%(self.numWater))

    
    def clickMilk(self):
        print("click Milk")
        if self.setMilk == False:
            self.MilkListNum = self.clickFlag
            self.clickFlag += 1
            self.setMilk = True
        self.numMilk += 1
        self.Orderlist[self.MilkListNum].setStyleSheet("border-image: url(./images/milk.png);")
        self.Numlist[self.MilkListNum].setText("%d 잔"%(self.numMilk))

    def clickShot(self):
        print("click Shot")
        if self.setShot == False:
            self.ShotListNum = self.clickFlag
            self.clickFlag += 1
            self.setShot = True
        self.numShot += 1
        self.Orderlist[self.ShotListNum].setStyleSheet("border-image: url(./images/shot.png);")
        self.Numlist[self.ShotListNum].setText("%d 잔"%(self.numShot))


    def clickOrder(self):
        self.second = SecondClass()
        # self.second.ButtonOK.clicked.connect(lambda: self.clickOK())
        
        self.numOfDrinks = {'아이스 아메리카노': self.numAme, '카페라떼': self.numLatte, '물': self.numWater, '우유': self.numMilk, '에스프레소': self.numShot}
        
        if self.numLatte + self.numAme + self.numWater + self.numMilk + self.numShot == 0:
            self.second.label.setText("주문을 입력하세요")

        else:
            self.orderNum += 1
            self.second.label.setText("주문이 완료되었습니다.")
            self.second.label_2.setText("주문번호: %d"%(self.orderNum))
            # modbus: write register
            
            settingLabel = ''
            for key, val in self.numOfDrinks.items():
                if val != 0:
                    settingLabel += (str(key)+': '+str(val)+'잔\n')

            self.second.label_3.setText(settingLabel)

            server.data_bank.set_holding_registers(0, [1, self.numAme, self.numLatte, self.numWater, self.numMilk, self.numShot])
            # server.data_bank.set_holding_registers(10, [int(self.orderNum), int(self.numAme), int(self.numLatte), int(self.numWater), int(self.numMilk), int(self.numShot)])
            print((server.data_bank.get_holding_registers(0, 6)))
            # server.stop()

            self.clickReset()

    # def clickOK(self):
    #     if server.data_bank.get_holding_registers(0, 1) != [0]:
    #         self.popup = PopupClass()
    #         # 비동기로 5초 후에 상태를 확인
    #         QTimer.singleShot(100, self.check_register_status)

    def check_register_status(self):
        # print(server.data_bank.get_holding_registers(0, 1))
        if server.data_bank.get_holding_registers(0, 1) == [0]:
            self.popup.close_popup()
        else:
            # 다시 상태를 확인 (예: 1초 후에 다시 확인)
            QTimer.singleShot(100, self.check_register_status)
            

    def clickReset(self):
        self.numAme = 0
        self.numLatte = 0
        self.numWater = 0
        self.numMilk = 0
        self.numShot = 0

        self.clickFlag = 0

        self.setAme = False
        self.setLatte = False
        self.setWater = False
        self.setMilk = False
        self.setShot = False

        self.AmeListNum = 0
        self.LatteListNum = 0
        self.WaterListNum = 0
        self.MilkListNum = 0
        self.ShotListNum = 0

        self.widget_2.setStyleSheet("color: white")
        self.widget_3.setStyleSheet("color: white")
        self.widget_4.setStyleSheet("color: white")
        self.widget_5.setStyleSheet("color: white")
        self.widget_6.setStyleSheet("color: white")
        self.num1.setText("")
        self.num2.setText("")
        self.num3.setText("")
        self.num4.setText("")
        self.num5.setText("")

            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WindowClass()
    # server.start()
    sys.exit(app.exec_())
   
   