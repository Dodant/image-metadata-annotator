#
# annotator.py
# image-metadata-annotator
#
# Created by Junggyun Oh on 03/06/2023.
# Copyright (c) 2023 Junggyun Oh All rights reserved.
#

import os
import os.path as pth
import sys
import random
import re
import math
import glob
import platform
from datetime import datetime

# import cv2
import numpy as np
# import pandas as pd

# import qimage2ndarray as q2n
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QRadioButton, QGroupBox, QHBoxLayout, QVBoxLayout, \
    QFileDialog, QLabel, QPushButton, QCheckBox, QButtonGroup, QMessageBox, QInputDialog, QSizePolicy


class Annotator(QWidget):
    def __init__(self):
        super().__init__()
        self.fname = '_'
        self.folderlabel = QLabel(f'Dataset Folder : {self.fname}', self)
        self.numberOfImageLabel = QLabel('Number of Images : _  |  Annotated : _')
        self.numberOfImageLabel.setAlignment(Qt.AlignLeading)
        self.fileNumName = QLabel(f'File : #_ | Current File Name : {self.fname}')

        self.weatherConditionBtnGroup = QButtonGroup()
        self.clear_btn = QRadioButton('Clear', self)
        self.cloud_btn = QRadioButton('Clouds', self)
        self.rain__btn = QRadioButton('Rain', self)
        self.foggy_btn = QRadioButton('Foggy', self)
        self.thder_btn = QRadioButton('Thunder', self)
        self.overc_btn = QRadioButton('Overcast', self)
        self.exsun_btn = QRadioButton('Extra Sunny', self)
        self.wcetc_btn = QRadioButton('ETC', self)

        self.timeStampBtnGroup = QButtonGroup()
        self.dawn__btn = QRadioButton('Dawn', self)
        self.mrndy_btn = QRadioButton('Morning to Day', self)
        self.eveng_btn = QRadioButton('Evening', self)
        self.night_btn = QRadioButton('Night', self)
        self.tsetc_btn = QRadioButton('ETC', self)

        self.inOutBtnGroup = QButtonGroup()
        self.indor_btn = QRadioButton('Indoor', self)
        self.outdr_btn = QRadioButton('outdoor', self)
        self.ioetc_btn = QRadioButton('ETC', self)

        self.initUI()


    def createWeatherConditionGroup(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.clear_btn, alignment=Qt.AlignLeading)
        vbox.addWidget(self.cloud_btn, alignment=Qt.AlignLeading)
        vbox.addWidget(self.rain__btn, alignment=Qt.AlignLeading)
        vbox.addWidget(self.foggy_btn, alignment=Qt.AlignLeading)
        vbox.addWidget(self.thder_btn, alignment=Qt.AlignLeading)
        vbox.addWidget(self.overc_btn, alignment=Qt.AlignLeading)
        vbox.addWidget(self.exsun_btn, alignment=Qt.AlignLeading)
        vbox.addWidget(self.wcetc_btn, alignment=Qt.AlignLeading)
        groupbox = QGroupBox('Weather Conditions')
        groupbox.setLayout(vbox)
        self.weatherConditionBtnGroup.setExclusive(True)
        self.weatherConditionBtnGroup.addButton(self.clear_btn, 1)
        self.weatherConditionBtnGroup.addButton(self.cloud_btn, 2)
        self.weatherConditionBtnGroup.addButton(self.rain__btn, 3)
        self.weatherConditionBtnGroup.addButton(self.foggy_btn, 4)
        self.weatherConditionBtnGroup.addButton(self.thder_btn, 5)
        self.weatherConditionBtnGroup.addButton(self.overc_btn, 6)
        self.weatherConditionBtnGroup.addButton(self.exsun_btn, 7)
        self.weatherConditionBtnGroup.addButton(self.wcetc_btn, 8)
        # self.weatherConditionBtnGroup.buttonClicked[int].connect(self.btnClicked)
        return groupbox

    def createTimeStampGroup(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.dawn__btn, alignment=Qt.AlignLeading)
        vbox.addWidget(self.mrndy_btn, alignment=Qt.AlignLeading)
        vbox.addWidget(self.eveng_btn, alignment=Qt.AlignLeading)
        vbox.addWidget(self.night_btn, alignment=Qt.AlignLeading)
        vbox.addWidget(self.tsetc_btn, alignment=Qt.AlignLeading)
        groupbox = QGroupBox('Time Stamp')
        groupbox.setLayout(vbox)
        self.timeStampBtnGroup.setExclusive(True)
        self.timeStampBtnGroup.addButton(self.dawn__btn, 1)
        self.timeStampBtnGroup.addButton(self.mrndy_btn, 2)
        self.timeStampBtnGroup.addButton(self.eveng_btn, 3)
        self.timeStampBtnGroup.addButton(self.night_btn, 4)
        self.timeStampBtnGroup.addButton(self.tsetc_btn, 5)
        # self.timeStampBtnGroup.buttonClicked[int].connect(self.btnClicked)
        return groupbox

    def createInOutdoorGroup(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.indor_btn, alignment=Qt.AlignCenter)
        vbox.addWidget(self.outdr_btn, alignment=Qt.AlignCenter)
        vbox.addWidget(self.ioetc_btn, alignment=Qt.AlignCenter)
        groupbox = QGroupBox('Indoor / Outdoor')
        groupbox.setLayout(vbox)
        self.timeStampBtnGroup.setExclusive(True)
        self.timeStampBtnGroup.addButton(self.indor_btn, 1)
        self.timeStampBtnGroup.addButton(self.outdr_btn, 2)
        self.timeStampBtnGroup.addButton(self.ioetc_btn, 3)
        # self.timeStampBtnGroup.buttonClicked[int].connect(self.btnClicked)
        return groupbox

    def fileDialogOpen(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fname = QFileDialog.getOpenFileName(self, 'Open File', options=options)[0]

    def extraDialog(self):
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Hello Out There")
            msgBox.setTextFormat(Qt.RichText)
            msg = "¯\\_(ツ)_/¯ \
                <br> Copyright (c) 2023 Junggyun Oh. All rights reserved. \
                <br> Please Report Bug and Additional Requirements Here. And Give Me Star. \
                <br> => <a href='https://github.com/Dodant/image-metadata-annotator'>Dodant/image-metadata-annotator</a>"
            msgBox.setText(msg)
            msgBox.exec()

    def initUI(self):
        self.fileDialogOpen()

        folderSelectBtn = QPushButton('Open Folder', self)
        folderSelectBtn.clicked.connect(self.fileDialogOpen)

        prevBtn = QPushButton('<<< << <', self)
        nextBtn = QPushButton('> >> >>>', self)
        recentBtn = QPushButton('Go to the Most Recently Annotated Image')
        # prevBtn.clicked.connect(self.goToPrevImage)
        # nextBtn.clicked.connect(self.goToNextImage)

        fhbox = QHBoxLayout()
        fhbox.addWidget(self.folderlabel, alignment=Qt.AlignCenter)
        fhbox.addWidget(folderSelectBtn, alignment=Qt.AlignCenter)

        mhbox = QHBoxLayout()
        mhbox.addWidget(prevBtn, alignment=Qt.AlignCenter)
        mhbox.addWidget(self.fileNumName, alignment=Qt.AlignCenter)
        mhbox.addWidget(nextBtn, alignment=Qt.AlignCenter)
        mhbox.addWidget(recentBtn, alignment=Qt.AlignCenter)

        timedoorbox = QVBoxLayout()
        timedoorbox.addWidget(self.createTimeStampGroup(), alignment=Qt.AlignCenter)
        timedoorbox.addWidget(self.createInOutdoorGroup(), alignment=Qt.AlignCenter)

        vhbox = QHBoxLayout()
        vhbox.addWidget(self.createWeatherConditionGroup(), alignment=Qt.AlignCenter)
        vhbox.addLayout(timedoorbox)

        vfbox = QVBoxLayout()
        vfbox.addLayout(fhbox)
        vfbox.addWidget(self.numberOfImageLabel, alignment=Qt.AlignCenter)
        vfbox.addLayout(mhbox)
        vfbox.addLayout(vhbox)

        self.setLayout(vfbox)
        self.setWindowTitle('Image Metadata Annotator')
        self.resize(1000, 800)
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':
    viewer = QApplication(sys.argv)
    ex = Annotator()
    sys.exit(viewer.exec_())
