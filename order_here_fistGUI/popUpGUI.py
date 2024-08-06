import os
import sys
import tkinter as tk

from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import*
from PyQt5 import uic
from PyQt5.QtTest import QTest

popup_class = uic.loadUiType("popup.ui")[0]

class PopupClass(QMainWindow, popup_class):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setupUi(self)
        self.setWindowTitle('Warning')
        self.label.setText("음료 제조 중입니다.\n잠시만 기다려 주세요.")

        self.movie = QMovie('./images/timer.gif', QByteArray(), self)
        self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self.movie.setScaledSize(QSize(140, 140))
        # QLabel에 동적 이미지 삽입
        self.label_2.setMovie(self.movie)
        self.movie.start()
        self.show()

    def close_popup(self):
        self.close()

