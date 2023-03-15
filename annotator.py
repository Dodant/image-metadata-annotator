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
import csv
import platform
from datetime import datetime

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QRadioButton, QGroupBox, QHBoxLayout, QVBoxLayout, \
    QLabel, QPushButton, QCheckBox, QButtonGroup, QMessageBox, QLineEdit


class Annotator(QWidget):
    def __init__(self):
        super().__init__()
        self.fname: str = ''
        self.dbpath, self.anpath = '', ''
        self.filepaths, self.filenames = [], []
        self.numOfImage = 0
        self.nowIndex: int = 0
        self.wthr, self.time, self.door, self.motion, self.illu = '', '', '', '', ''

        self.folderlabel = QLabel('Dataset Folder :', self)
        self.folderInput = QLineEdit(self)
        self.ok_checkbtn = QCheckBox('Integrity Check', self)
        self.folderSelectBtn = QPushButton('Click', self)

        self.numberOfImageLabel = QLabel('You should copy & paste your folder path like below.')
        self.isAnnotatedLbl = QLabel('Annotated')
        self.fileNumName = QLabel('EX) /home/username/Downloads/datasets')

        self.pixmap = QPixmap()
        self.lbl_img = QLabel()

        self.inoutList = ['indoor', 'outdoor', 'etc']
        self.wthrCndtList = ['clear', 'clouds', 'rain', 'foggy', 'thunder', 'overcast', 'extra_sunny', 'etc']
        self.timeStampList = ['dawn', 'morning_to_day', 'evening', 'night', 'etc']
        self.motionList = ['o', 'x']
        self.illuList = ['bright', 'dim', 'dark']
        self.headerList = ['id', 'image_path', 'annotated', 'in_out',
                           'weather', 'time', 'motion_blur', 'illuminance', 'last_modified']
        self.extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.tif', '.tiff']
        self.csvRows = []

        self.inOutBtnGrp = QButtonGroup()
        self.wthrCndtBtnGrp = QButtonGroup()
        self.timeStampBtnGrp = QButtonGroup()
        self.motionBtnGrp = QButtonGroup()
        self.illuBtnGrp = QButtonGroup()

        self.initUI()

    def folderOpen(self):
        self.dbpath = self.folderInput.text()
        self.anpath = pth.join(self.dbpath, 'annotation.csv')
        self.filepaths, self.filenames = self.getAllImageFilePath(self.extensions, self.dbpath)
        self.numOfImage = len(self.filepaths)

        if not self.filepaths:
            self.warnMsgDialog('No Image. <br> Check the Directory Paths Once More.')
            return
        
        self.ok_checkbtn.setChecked(True)
        self.ok_checkbtn.setEnabled(False)
        self.initMetadataCSV()
        self.changeImageAndInfo()
        self.checkedBtnManage()

    def initMetadataCSV(self):
        if pth.exists(self.anpath):
            with open(self.anpath, 'r', newline='') as f:
                self.csvRows = list(csv.reader(f))[1:]
            return
        
        for idx, item in enumerate(self.filepaths):
            item = pth.join(*item.split(pth.sep)[item.split(pth.sep).index(pth.basename(self.dbpath)):])
            self.csvRows.append([idx, item, 'N', '', '', '', '', '', 0])
            
        with open(self.anpath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.headerList)
            writer.writerows(self.csvRows)

    def goToRecentAnnotatedImage(self):
        self.nowIndex = np.argmax([i[-1] for i in self.csvRows])
        self.changeImageAndInfo()
        self.checkedBtnManage()

    def saveMetadataToCSV(self):
        if not self.filepaths:
            self.warnMsgDialog('You must import dataset.')
            return

        if self.wthrCndtBtnGrp.checkedId() == -1 or self.timeStampBtnGrp.checkedId() == -1 or \
                self.inOutBtnGrp.checkedId() == -1 or self.motionBtnGrp.checkedId() == -1 or \
                self.illuBtnGrp.checkedId() == -1:
            self.warnMsgDialog('You have to check all groups')
            return

        item = self.filepaths[self.nowIndex]
        item = pth.join(*item.split(pth.sep)[item.split(pth.sep).index(pth.basename(self.folderInput.text())):])

        with open(self.anpath, 'r', newline='') as f: self.csvRows = list(csv.reader(f))[1:]
        new_row_data = [self.nowIndex, item, 'Y', self.door, self.wthr, self.time,
                        self.motion, self.illu, int(datetime.now().strftime('%Y%m%d%H%M%S'))]
        self.csvRows[self.nowIndex] = new_row_data

        with open(self.anpath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.headerList)
            writer.writerows(self.csvRows)
        self.checkAnnotated()

    @staticmethod
    def warnMsgDialog(msg):
        msgBox = QMessageBox()
        msgBox.setWindowTitle('Something Went Wrong')
        msgBox.setTextFormat(Qt.RichText)
        msgBox.setText(msg)
        msgBox.exec()

    @staticmethod
    def getAllImageFilePath(extensions, folder_path: str) -> (list, list):
        filepaths, filenames = [], []
        for path, dirs, files in os.walk(folder_path):
            for file in files:
                if pth.splitext(file)[1].lower() in extensions:
                    filepaths.append(pth.join(path, file))
                    filenames.append(file)
        return filepaths, filenames

    def createGroup(self, title: str, btnNameList: list, btnGroup, w: int, h: int):
        vbox = QVBoxLayout()
        groupbox = QGroupBox(title)
        groupbox.setLayout(vbox)
        groupbox.setFixedSize(w, h)

        for id, item in enumerate(btnNameList):
            if self.wthrCndtList == btnNameList: id += 10
            if self.timeStampList == btnNameList: id += 20
            if self.motionList == btnNameList: id += 30
            if self.illuList == btnNameList: id += 40

            title = item.replace('_', ' ').title() if item != 'etc' else item.upper()
            btn = QRadioButton(title)
            btnGroup.addButton(btn, id)
            vbox.addWidget(btn, alignment=Qt.AlignLeading)

        btnGroup.setExclusive(True)
        btnGroup.buttonClicked[int].connect(self.btnClicked)
        return groupbox

    def extraDialog(self):
        msg = "¯\\_(ツ)_/¯ \
                <br> Copyright (c) 2023 Junggyun Oh. All rights reserved. \
                <br> Please Report Bug and Additional Requirements Here. And Give Me Star. \
                <br> => <a href='https://github.com/Dodant/image-metadata-annotator'>Dodant/image-metadata-annotator</a>"
        self.warnMsgDialog(msg)

    def changeImageAndInfo(self):
        self.fname = self.filenames[self.nowIndex]
        self.pixmap = QPixmap(self.filepaths[self.nowIndex]).scaled(1280, 720)
        self.lbl_img.setPixmap(self.pixmap)
        self.checkAnnotated()
        self.fileNumName.setText(f'File : #{self.nowIndex + 1} / {self.numOfImage:<15}Name : {self.fname}')

    def checkAnnotated(self):
        annotated = len([i for i in self.csvRows if i[2] == 'Y'])
        anno_chck = self.csvRows[self.nowIndex][2]
        msg = f'Num of Annotated / Images : {annotated} / {self.numOfImage}{"&nbsp;"*12}Is It Annotated? : '
        msg += f'<b><span style = "color:{"blue" if anno_chck == "Y" else "red"}">{anno_chck}</span></b>'
        self.numberOfImageLabel.setText(msg)

    def btnClicked(self, btn):
        if not self.filepaths:
            self.warnMsgDialog('You must import dataset.')
            return

        grp, idx = divmod(btn, 10)
        if grp == 0:
            if idx == 0:
                self.door = self.inoutList[idx]
                self.time = self.timeStampList[-1]
                self.wthr = self.wthrCndtList[-1]
                self.wthrCndtBtnGrp.button(17).setChecked(True)
                self.timeStampBtnGrp.button(24).setChecked(True)
            else:
                self.door = self.inoutList[idx]
        if grp == 1: self.wthr = self.wthrCndtList[idx]
        if grp == 2: self.time = self.timeStampList[idx]
        if grp == 3: self.motion = self.motionList[idx]
        if grp == 4: self.illu = self.illuList[idx]

    def checkedBtnManage(self):
        bgList = [self.inOutBtnGrp, self.wthrCndtBtnGrp, self.timeStampBtnGrp, self.motionBtnGrp, self.illuBtnGrp]
        if self.csvRows[self.nowIndex][2] == 'Y':
            self.inOutBtnGrp.button(self.inoutList.index(self.csvRows[self.nowIndex][3])).setChecked(True)
            self.wthrCndtBtnGrp.button(self.wthrCndtList.index(self.csvRows[self.nowIndex][4])+10).setChecked(True)
            self.timeStampBtnGrp.button(self.timeStampList.index(self.csvRows[self.nowIndex][5])+20).setChecked(True)
            self.motionBtnGrp.button(self.motionList.index(self.csvRows[self.nowIndex][6])+30).setChecked(True)
            self.illuBtnGrp.button(self.illuList.index(self.csvRows[self.nowIndex][7])+40).setChecked(True)
        else:
            for bg in bgList:
                bg.setExclusive(False)
                for btn in bg.buttons(): btn.setChecked(False)
                bg.setExclusive(True)

    def goToPrevImage(self):
        self.nowIndex -= 1
        if self.nowIndex < 0: self.nowIndex = self.numOfImage - 1
        self.changeImageAndInfo()
        self.checkedBtnManage()

    def goToNextImage(self):
        self.nowIndex += 1
        if self.nowIndex >= self.numOfImage: self.nowIndex = 0
        self.changeImageAndInfo()
        self.checkedBtnManage()

    def initUI(self):
        self.folderInput.setFixedWidth(350)
        self.ok_checkbtn.setEnabled(False)
        self.numberOfImageLabel.setAlignment(Qt.AlignCenter)
        self.folderSelectBtn.clicked.connect(self.folderOpen)

        width = 180
        savebtn = QPushButton('Save Metadata (S)', self)
        savebtn.setFixedWidth(width)
        savebtn.clicked.connect(self.saveMetadataToCSV)

        extraBtn = QPushButton('Hello Out There', self)
        extraBtn.clicked.connect(self.extraDialog)

        prevBtn = QPushButton('<<< << < (A)', self)
        nextBtn = QPushButton('(D) > >> >>>', self)
        recentBtn = QPushButton('Jump to Recently Annotated Image')
        prevBtn.clicked.connect(self.goToPrevImage)
        nextBtn.clicked.connect(self.goToNextImage)
        recentBtn.clicked.connect(self.goToRecentAnnotatedImage)

        fhbox = QHBoxLayout()
        fhbox.addStretch(1)
        fhbox.addWidget(self.folderlabel, alignment=Qt.AlignCenter)
        fhbox.addWidget(self.folderInput, alignment=Qt.AlignCenter)
        fhbox.addWidget(self.folderSelectBtn, alignment=Qt.AlignCenter)
        fhbox.addStretch(1)

        mbbox = QHBoxLayout()
        mbbox.addStretch(1)
        mbbox.addWidget(self.numberOfImageLabel, alignment=Qt.AlignCenter)
        mbbox.addStretch(1)
        mbbox.addWidget(self.ok_checkbtn, alignment=Qt.AlignCenter)
        mbbox.addStretch(1)

        mhbox = QHBoxLayout()
        mhbox.addWidget(prevBtn, alignment=Qt.AlignCenter)
        mhbox.addWidget(nextBtn, alignment=Qt.AlignCenter)
        mhbox.addWidget(self.fileNumName, alignment=Qt.AlignCenter)
        mhbox.addStretch(1)
        mhbox.addWidget(recentBtn, alignment=Qt.AlignCenter)

        gls = ['Indoor / Outdoor', 'Weather Conditions', 'Time Stamp', 'Motion Blur', 'Illuminance']
        lls = [self.inoutList, self.wthrCndtList, self.timeStampList, self.motionList, self.illuList]
        rls = [self.inOutBtnGrp, self.wthrCndtBtnGrp, self.timeStampBtnGrp, self.motionBtnGrp, self.illuBtnGrp]
        hls = [100, 240, 160, 80, 110]

        checkgroupbox = QVBoxLayout()
        for g, l, r, h in zip(gls, lls, rls, hls):
            checkgroupbox.addWidget(self.createGroup(g, l, r, width, h), alignment=Qt.AlignCenter)
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

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_A: self.goToPrevImage()
        if e.key() == Qt.Key_D: self.goToNextImage()
        if e.key() == Qt.Key_S: self.saveMetadataToCSV()
        if e.key() == Qt.Key_E: self.goToRecentAnnotatedImage()
        if e.key() == Qt.Key_Return: self.folderOpen()


if __name__ == '__main__':
    viewer = QApplication(sys.argv)
    ex = Annotator()
    sys.exit(viewer.exec_())
