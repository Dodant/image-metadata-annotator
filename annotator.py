#
# annotator.py
# image-metadata-annotator
#
# Created by Junggyun Oh on 03/06/2023.
# Copyright (c) 2023 Junggyun Oh All rights reserved.
#

import os
import sys
import csv

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QRadioButton, QGroupBox, QHBoxLayout, QVBoxLayout, \
    QLabel, QPushButton, QCheckBox, QButtonGroup, QMessageBox, QLineEdit


class Annotator(QWidget):
    def __init__(self):
        super().__init__()
        self.fname: str = '_'
        self.filepaths: list = []
        self.filenames: list = []
        self.nowIndex: int = 0
        self.numberOfAnnotated: int = 0
        self.isAnnotated: bool = False

        self.folderlabel = QLabel(f'Dataset Folder :', self)
        self.folderInput = QLineEdit(self)
        self.ok_checkbtn = QCheckBox('OK', self)
        self.info_checkbtn = QCheckBox('Metadata Exists', self)
        self.numberOfImageLabel = QLabel('No. of Images : _  ||  No. of Annotated File : _  ||  Is Annotated? : _')
        self.isAnnotatedLbl = QLabel('Annotated')
        self.fileNumName = QLabel(f'File : #_  ||  Current File Name : {self.fname}')

        self.pixmap = QPixmap()
        self.lbl_img = QLabel()

        self.wthrCndtList = ['clear', 'clouds', 'rain', 'foggy', 'thunder', 'overcast', 'extra_sunny', 'etc']
        self.timeStampList = ['dawn', 'morning_to_day', 'evening', 'night', 'etc']
        self.inoutList = ['indoor', 'outdoor', 'etc']

        self.wthrCndtBtnGroup = QButtonGroup()
        self.timeStampBtnGroup = QButtonGroup()
        self.inOutBtnGroup = QButtonGroup()

        self.initUI()

    @staticmethod
    def getAllImageFilePath(folder_path:str) -> (list, list):
        filepaths, filenames = [], []
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.tif', '.tiff']
        for path, dirs, files in os.walk(folder_path):
            for file in files:
                if os.path.splitext(file)[1].lower() in extensions:
                    filepaths.append(os.path.join(path, file))
                    filenames.append(file)
        return filepaths, filenames

    @staticmethod
    def createGroup(title:str, btnNameList:list, btnGroup, w:int, h:int):
        vbox = QVBoxLayout()
        btnGroup.setExclusive(True)
        groupbox = QGroupBox(title)
        groupbox.setLayout(vbox)
        groupbox.setFixedSize(w, h)
        for idx, item in enumerate(btnNameList):
            title = item.replace('_', ' ').title() if item != 'etc' else 'ETC'
            btn = QRadioButton(title)
            btnGroup.addButton(btn, idx)
            vbox.addWidget(btn, alignment=Qt.AlignLeading)
        # btnGroup.buttonClicked[int].connect(self.btnClicked)
        return groupbox

    @staticmethod
    def extraDialog():
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Hello Out There")
        msgBox.setTextFormat(Qt.RichText)
        msg = "¯\\_(ツ)_/¯ \
                <br> Copyright (c) 2023 Junggyun Oh. All rights reserved. \
                <br> Please Report Bug and Additional Requirements Here. And Give Me Star. \
                <br> => <a href='https://github.com/Dodant/image-metadata-annotator'>Dodant/image-metadata-annotator</a>"
        msgBox.setText(msg)
        msgBox.exec()

    def changeImageAndInfo(self):
        self.fname = self.filenames[self.nowIndex]
        self.pixmap = QPixmap(self.filepaths[self.nowIndex]).scaled(1000, 750)
        self.lbl_img.setPixmap(self.pixmap)
        self.checkAnnotated()
        self.fileNumName.setText(f'File : #{self.nowIndex + 1}  ||  Current File Name : {self.fname}')

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
        self.initMetadataCSV()
        self.changeImageAndInfo()

    def checkAnnotated(self):
        msg = f'No. of Images : {len(self.filepaths)}  '
        msg += f'||  No. of Annotated File : {self.numberOfAnnotated}  '
        msg += f'||  Is Annotated? : {"Y" if self.isAnnotated else "N"}'
        self.numberOfImageLabel.setText(msg)

    def saveMetadataToCSV(self):
        new_row_data = [self.nowIndex, self.filepaths[self.nowIndex], False, '', '', '', '']
        with open('example.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
        rows[self.nowIndex+1] = new_row_data
        with open('annotation.csv','w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(rows)

    def initMetadataCSV(self):
        header_list = ['id','image_path','annotated','weather','time','in_out','last_modified']
        with open('annotation.csv','w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header_list)
            for idx, item in self.filepaths:
                writer.writerow([idx, item, False, '', '', '', ''])

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
        recentBtn = QPushButton('Jump to Recently Annotated Image')
        prevBtn.clicked.connect(self.goToImage)
        nextBtn.clicked.connect(self.goToImage)

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
        mhbox.addWidget(prevBtn, alignment=Qt.AlignCenter)
        mhbox.addWidget(nextBtn, alignment=Qt.AlignCenter)
        mhbox.addWidget(self.fileNumName, alignment=Qt.AlignCenter)
        mhbox.addStretch(1)
        mhbox.addWidget(recentBtn, alignment=Qt.AlignCenter)

        checkgroupbox = QVBoxLayout()
        checkgroupbox.addWidget(
            self.createGroup('Weather Conditions', self.wthrCndtList, self.wthrCndtBtnGroup, 150, 230),
            alignment=Qt.AlignCenter)
        checkgroupbox.addWidget(
            self.createGroup('Time Stamp', self.timeStampList, self.timeStampBtnGroup, 150, 160),
            alignment=Qt.AlignCenter)
        checkgroupbox.addWidget(
            self.createGroup('Indoor / Outdoor', self.inoutList, self.inOutBtnGroup, 150, 100),
            alignment=Qt.AlignCenter)
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

    def goToImage(self):
        if not self.filepaths: return
        sender = self.sender()
        if sender.text() == '<<< << <':
            self.nowIndex -= 1
            if self.nowIndex < 0: self.nowIndex = len(self.filepaths) - 1
        elif sender.text() == '> >> >>>':
            self.nowIndex += 1
            if self.nowIndex >= len(self.filepaths): self.nowIndex = 0
        self.changeImageAndInfo()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_A: self.goToImage()
        if e.key() == Qt.Key_D: self.goToImage()
        if e.key() in [Qt.Key_Enter, Qt.Key_S]: pass


if __name__ == '__main__':
    viewer = QApplication(sys.argv)
    ex = Annotator()
    sys.exit(viewer.exec_())
