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
    QFileDialog, QLabel, QPushButton, QCheckBox, QButtonGroup, QMessageBox, QInputDialog, QSizePolicy, QLineEdit


class Annotator(QWidget):
    def __init__(self):
        super().__init__()
        self.fname: str = '_'
        self.filepaths: list = []
        self.filenames: list = []
        self.nowIndex: int = 0

        self.folderlabel = QLabel(f'Dataset Folder :', self)
        self.folderInput = QLineEdit(self)
        self.ok_checkbtn = QCheckBox('OK', self)
        self.info_checkbtn = QCheckBox('Metadata Exists', self)
        self.numberOfImageLabel = QLabel('Number of Images : _  |  Annotated : _')
        self.fileNumName = QLabel(f'File : #_ | Current File Name : {self.fname}')

        self.pixmap = QPixmap()
        self.lbl_img = QLabel()

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
        self.outdr_btn = QRadioButton('Outdoor', self)
        self.ioetc_btn = QRadioButton('ETC', self)

        self.initUI()

    @staticmethod
    def getAllImageFilePath(folder_path: str) -> (list, list):
        filepaths, filenames = [], []
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.tif', '.tiff']
        for path, dirs, files in os.walk(folder_path):
            for file in files:
                if os.path.splitext(file)[1].lower() in extensions:
                    filepaths.append(os.path.join(path, file))
                    filenames.append(file)
        return filepaths, filenames

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
        groupbox.setFixedSize(150, 230)
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
        groupbox.setFixedSize(150, 160)
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
        vbox.addWidget(self.indor_btn, alignment=Qt.AlignLeading)
        vbox.addWidget(self.outdr_btn, alignment=Qt.AlignLeading)
        vbox.addWidget(self.ioetc_btn, alignment=Qt.AlignLeading)
        groupbox = QGroupBox('Indoor / Outdoor')
        groupbox.setLayout(vbox)
        groupbox.setFixedSize(150,100)
        self.inOutBtnGroup.setExclusive(True)
        self.inOutBtnGroup.addButton(self.indor_btn, 1)
        self.inOutBtnGroup.addButton(self.outdr_btn, 2)
        self.inOutBtnGroup.addButton(self.ioetc_btn, 3)
        # self.timeStampBtnGroup.buttonClicked[int].connect(self.btnClicked)
        return groupbox

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

    def folderOpen(self):
        self.filepaths, self.filenames = self.getAllImageFilePath(self.folderInput.text())
        if not self.filepaths:
            msgBox = QMessageBox()
            msgBox.setWindowTitle('Something Went Wrong')
            msgBox.setTextFormat(Qt.RichText)
            msgBox.setText('No Image. <br> Check the Directory Paths Once More.')
            msgBox.exec()
            return
        self.ok_checkbtn.setChecked(True)
        self.nowIndex = 0
        self.fname = self.filenames[self.nowIndex]
        self.pixmap = QPixmap(self.filepaths[self.nowIndex]).scaled(1000, 750)
        self.lbl_img.setPixmap(self.pixmap)
        self.numberOfImageLabel.setText(f'Number of Images : {len(self.filepaths)}  |  Annotated : {0}')
        self.fileNumName.setText(f'File : #{self.nowIndex} | Current File Name : {self.fname}')

    def initUI(self):

        self.folderInput.setFixedWidth(350)
        self.ok_checkbtn.setEnabled(False)
        self.info_checkbtn.setEnabled(False)
        self.numberOfImageLabel.setAlignment(Qt.AlignCenter)

        savebtn = QPushButton('Save Metadata', self)
        savebtn.setFixedWidth(150)
        # savebtn.clicked.connect(self.saveMetadataToCSV)

        extraBtn = QPushButton('Hello Out There', self)
        extraBtn.clicked.connect(self.extraDialog)

        folderSelectBtn = QPushButton('Click', self)
        folderSelectBtn.clicked.connect(self.folderOpen)

        prevBtn = QPushButton('<<< << <', self)
        nextBtn = QPushButton('> >> >>>', self)
        recentBtn = QPushButton('Go to the Most Recently Annotated Image')
        prevBtn.clicked.connect(self.goToPrevImage)
        nextBtn.clicked.connect(self.goToNextImage)

        fhbox = QHBoxLayout()
        fhbox.addStretch(1)
        fhbox.addWidget(self.folderlabel, alignment=Qt.AlignCenter)
        fhbox.addWidget(self.folderInput, alignment=Qt.AlignCenter)
        fhbox.addWidget(folderSelectBtn, alignment=Qt.AlignCenter)
        fhbox.addStretch(1)

        mbbox = QHBoxLayout()
        mbbox.addStretch(1)
        mbbox.addWidget(self.numberOfImageLabel, alignment=Qt.AlignCenter)
        mbbox.addStretch(1)
        mbbox.addWidget(self.ok_checkbtn, alignment=Qt.AlignCenter)
        mbbox.addWidget(self.info_checkbtn, alignment=Qt.AlignCenter)
        mbbox.addStretch(1)

        mhbox = QHBoxLayout()
        mhbox.addStretch(1)
        mhbox.addWidget(prevBtn, alignment=Qt.AlignCenter)
        mhbox.addWidget(self.fileNumName, alignment=Qt.AlignCenter)
        mhbox.addWidget(nextBtn, alignment=Qt.AlignCenter)
        mhbox.addStretch(1)
        mhbox.addWidget(recentBtn, alignment=Qt.AlignCenter)
        mhbox.addStretch(1)

        checkgroupbox = QVBoxLayout()
        checkgroupbox.addWidget(self.createWeatherConditionGroup(), alignment=Qt.AlignCenter)
        checkgroupbox.addWidget(self.createTimeStampGroup(), alignment=Qt.AlignCenter)
        checkgroupbox.addWidget(self.createInOutdoorGroup(), alignment=Qt.AlignCenter)
        checkgroupbox.addWidget(savebtn, alignment=Qt.AlignCenter)
        checkgroupbox.addStretch(1)

        vhbox = QHBoxLayout()
        vhbox.addWidget(self.lbl_img)
        vhbox.addLayout(checkgroupbox)

        hhbox = QHBoxLayout()
        hhbox.addStretch(1)
        hhbox.addWidget(extraBtn, alignment=Qt.AlignCenter)
        hhbox.addStretch(1)

        vfbox = QVBoxLayout()
        vfbox.addStretch(1)
        vfbox.addLayout(fhbox)
        vfbox.addLayout(mbbox)
        vfbox.addLayout(mhbox)
        vfbox.addStretch(1)
        vfbox.addLayout(vhbox)
        vfbox.addStretch(1)
        vfbox.addLayout(hhbox)

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

    def goToPrevImage(self):
        if not self.filepaths: return
        self.nowIndex -= 1
        if self.nowIndex < 0: self.nowIndex = len(self.filepaths) - 1
        self.fname = self.filenames[self.nowIndex]
        self.pixmap = QPixmap(self.filepaths[self.nowIndex]).scaled(1000, 750)
        self.lbl_img.setPixmap(self.pixmap)
        self.numberOfImageLabel.setText(f'Number of Images : {len(self.filepaths)}  |  Annotated : {0}')
        self.fileNumName.setText(f'File : #{self.nowIndex} | Current File Name : {self.fname}')
        # self.changeImageAtAllOnce()

    def goToNextImage(self):
        if not self.filepaths: return
        self.nowIndex += 1
        if self.nowIndex >= len(self.filepaths): self.nowIndex = 0
        self.fname = self.filenames[self.nowIndex]
        self.pixmap = QPixmap(self.filepaths[self.nowIndex]).scaled(1000, 750)
        self.lbl_img.setPixmap(self.pixmap)
        self.numberOfImageLabel.setText(f'Number of Images : {len(self.filepaths)}  |  Annotated : {0}')
        self.fileNumName.setText(f'File : #{self.nowIndex} | Current File Name : {self.fname}')
        # self.changeImageAtAllOnce()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_A: self.goToPrevImage()
        if e.key() == Qt.Key_D: self.goToNextImage()


if __name__ == '__main__':
    viewer = QApplication(sys.argv)
    ex = Annotator()
    sys.exit(viewer.exec_())
