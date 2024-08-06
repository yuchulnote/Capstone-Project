# GUI Test
import os
import sys
import tkinter as tk

from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import*
from PyQt5 import uic
from PyQt5.QtTest import QTest

second_class = uic.loadUiType("order_fin.ui")[0]

class SecondClass(QMainWindow, second_class):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setupUi(self)
        self.setWindowTitle('ORDER HERE')
        self.setInitStyle_2()
        self.show()

    def setInitStyle_2(self):
        self.ButtonOK.clicked.connect(lambda: self.clickOK())
    
    def clickOK(self):
        self.close()
        
