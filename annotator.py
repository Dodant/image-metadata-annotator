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
from datetime import datetime

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QRadioButton, QGroupBox, QHBoxLayout, QVBoxLayout, \
    QLabel, QPushButton, QCheckBox, QButtonGroup, QMessageBox, QLineEdit


class Annotator(QWidget):
    def __init__(self):
        super().__init__()
        self.initialize_variables()
        self.create_widgets()
        self.init_ui()

    def initialize_variables(self):
        self.file_name = ''
        self.db_path = ''
        self.annotation_path = ''
        self.file_paths = []
        self.file_names = []
        self.image_count = 0
        self.current_index = 0

        self.weather = ''
        self.time_of_day = ''
        self.indoor_outdoor = ''
        self.motion_blur = ''
        self.illumination = ''

        self.indoor_outdoor_list = ['indoor', 'outdoor', 'etc']
        self.weather_condition_list = ['clear','clouds','rain','foggy','thunder','overcast','extra_sunny','etc']
        self.time_of_day_list = ['dawn', 'morning_to_day', 'evening', 'night', 'etc']
        self.motion_list = ['o', 'x']
        self.illumination_list = ['bright', 'dim', 'dark']
        self.header_list = ['id', 'image_path', 'annotated', 'in_out',
                            'weather', 'time_of_day', 'motion_blur', 'illuminance', 'last_modified']
        self.extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.tif', '.tiff']
        self.csv_rows = []

    def create_widgets(self):
        self.folder_label = QLabel('Dataset Folder :', self)
        self.folder_input = QLineEdit(self)
        self.integrity_check_btn = QCheckBox('Integrity Check', self)
        self.folder_select_btn = QPushButton('Click', self)

        self.number_of_image_label = QLabel('Please copy and paste your folder path as shown below.')
        self.is_annotated_label = QLabel('Annotated')
        self.file_num_name = QLabel('EX) /home/user/Downloads/datasets')

        self.pixmap = QPixmap()
        self.image_label = QLabel()

        self.indoor_outdoor_btn_grp = QButtonGroup()
        self.weather_condition_btn_grp = QButtonGroup()
        self.time_of_day_btn_grp = QButtonGroup()
        self.motion_btn_grp = QButtonGroup()
        self.illumination_btn_grp = QButtonGroup()

    def open_folder(self):
        self.db_path = self.folder_input.text()
        self.annotation_path = pth.join(self.db_path, 'annotation.csv')
        self.file_paths, self.file_names = self.get_all_image_file_paths(self.extensions, self.db_path)
        self.image_count = len(self.file_paths)

        if not self.file_paths:
            return self.display_warning_message('No image found. <br> Please double-check the directory paths.')
        
        self.integrity_check_btn.setChecked(True)
        self.integrity_check_btn.setEnabled(False)
        self.init_metadata_csv()
        self.update_image_and_info()
        self.manage_checked_buttons()

    def init_metadata_csv(self):
        if pth.exists(self.annotation_path):
            with open(self.annotation_path, 'r', newline='') as f:
                self.header_list = list(csv.reader(f))[1:]
            return

        for idx, item in enumerate(self.file_paths):
            item = pth.join(*item.split(pth.sep)[item.split(pth.sep).index(pth.basename(self.db_path)):])
            self.header_list.append([idx, item, 'N', '', '', '', '', '', 0])

        with open(self.annotation_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.header_list)
            writer.writerows(self.header_list)

    def navigate_to_recently_annotated_image(self):
        self.current_index = np.argmax([i[-1] for i in self.header_list])
        self.update_image_and_info()
        self.manage_checked_buttons()

    def save_metadata_to_csv(self):
        if not self.file_paths:
            return self.display_warning_message('You must import dataset.')

        if self.is_any_group_unchecked():
            return self.display_warning_message('You have to check all groups')

        item = self.get_relative_file_path()

        with open(self.annotation_path, 'r', newline='') as f:
            self.header_list = list(csv.reader(f))[1:]
        new_row_data = self.create_new_row_data()
        self.header_list[self.current_index] = new_row_data

        self.write_metadata_to_csv()
        self.check_annotated()

    def is_any_group_unchecked(self):
        return (self.weather_condition_btn_grp  .checkedId() == -1 or
                self.time_of_day_btn_grp        .checkedId() == -1 or
                self.indoor_outdoor_btn_grp     .checkedId() == -1 or
                self.motion_btn_grp             .checkedId() == -1 or
                self.illumination_btn_grp       .checkedId() == -1)

    def get_relative_file_path(self):
        item = self.file_paths[self.current_index]
        return pth.join(*item.split(pth.sep)[item.split(pth.sep).index(pth.basename(self.folder_input.text())):])

    def create_new_row_data(self):
        current_time = int(datetime.now().strftime('%Y%m%d%H%M%S'))
        return [
            self.current_index,
            self.get_relative_file_path(),
            'Y',
            self.indoor_outdoor,
            self.weather,
            self.time_of_day,
            self.motion_blur,
            self.illumination,
            current_time
        ]

    @staticmethod
    def display_warning_message(msg):
        msg_box = QMessageBox()
        msg_box.setWindowTitle('Something Went Wrong')
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(msg)
        msg_box.exec()

    @staticmethod
    def get_all_image_file_paths(extensions, folder_path: str) -> (list, list):
        file_paths, file_names = [], []
        for path, dirs, files in os.walk(folder_path):
            for file in files:
                if pth.splitext(file)[1].lower() in extensions:
                    file_paths.append(pth.join(path, file))
                    file_names.append(file)
        return file_paths, file_names

    def create_group(self, title: str, btn_name_list: list, btn_grp, w: int, h: int):
        vbox = QVBoxLayout()
        groupbox = QGroupBox(title)
        groupbox.setLayout(vbox)
        groupbox.setFixedSize(w, h)

        for id, item in enumerate(btn_name_list):
            if self.weather_condition_list  == btn_name_list: id += 10
            if self.time_of_day_list        == btn_name_list: id += 20
            if self.motion_list             == btn_name_list: id += 30
            if self.illumination_list       == btn_name_list: id += 40

            title = item.replace('_', ' ').title() if item != 'etc' else item.upper()
            btn = QRadioButton(title)
            btn_grp.addButton(btn, id)
            vbox.addWidget(btn, alignment=Qt.AlignLeading)

        btn_grp.setExclusive(True)
        btn_grp.buttonClicked[int].connect(self.handle_button_click)
        return groupbox

    def show_extra_dialog(self):
        msg = "¯\\_(ツ)_/¯ \
                <br> Copyright &copy; 2023 Junggyun Oh. All rights reserved. \
                <br> Please report bugs and additional requirements here. Your feedback is appreciated.  \
                <br> => <a href='https://github.com/Dodant/image-metadata-annotator'>Dodant/image-metadata-annotator</a>"
        self.display_warning_message(msg)

    def update_image_and_info(self):
        self.file_name = self.file_names[self.current_index]
        self.pixmap = QPixmap(self.file_paths[self.current_index]).scaled(1280, 720)
        self.image_label.setPixmap(self.pixmap)
        self.update_file_num_name()
        self.update_number_of_image_label()

    def update_file_num_name(self):
        file_num_name_text = f'File : #{self.current_index + 1} / {self.image_count:<15}Name : {self.file_name}'
        self.file_num_name.setText(file_num_name_text)

    def update_number_of_image_label(self):
        annotated_count = sum(1 for _, _, annotated in self.header_list if annotated == 'Y')
        is_annotated = self.header_list[self.current_index][2]
        color = 'blue' if is_annotated == 'Y' else 'red'
        number_of_image_label_text = (
            f'# of Annotated / Images : {annotated_count} / {self.image_count}{"&nbsp;" * 12}Is It Annotated? : '
            f'<b><span style="color:{color}">{is_annotated}</span></b>'
        )
        self.number_of_image_label.setText(number_of_image_label_text)

    def handle_button_click(self, btn):
        if not self.file_paths:
            return self.display_warning_message('You must import dataset.')

        grp, idx = divmod(btn, 10)
        if grp == 0: self.set_indoor_outdoor(idx)
        elif grp == 1: self.weather     = self.weather_condition_list[idx]
        elif grp == 2: self.time_of_day = self.time_of_day_list[idx]
        elif grp == 3: self.motion_blur = self.motion_list[idx]
        elif grp == 4: self.illu        = self.illumination_list[idx]

    def set_indoor_outdoor(self, idx):
        if idx == 0:
            self.indoor_outdoor = self.indoor_outdoor_list[idx]
            self.time_of_day    = self.time_of_day_list[-1]
            self.weather        = self.weather_condition_list[-1]
            self.weather_condition_btn_grp.button(17).setChecked(True)
            self.time_of_day_btn_grp.button(24).setChecked(True)
        else:
            self.indoor_outdoor = self.indoor_outdoor_list[idx]

    def manage_checked_buttons(self):
        btn_grp_list = [
            self.indoor_outdoor_btn_grp,
            self.weather_condition_btn_grp,
            self.time_of_day_btn_grp,
            self.motion_btn_grp,
            self.illumination_btn_grp
        ]
        if self.header_list[self.current_index][2] == 'Y':
            self.indoor_outdoor_btn_grp.button(
                self.indoor_outdoor_list.index(self.header_list[self.current_index][3])).setChecked(True)
            self.weather_condition_btn_grp.button(
                self.weather_condition_list.index(self.header_list[self.current_index][4])+10).setChecked(True)
            self.time_of_day_btn_grp.button(
                self.time_of_day_list.index(self.header_list[self.current_index][5])+20).setChecked(True)
            self.motion_btn_grp.button(
                self.motion_list.index(self.header_list[self.current_index][6])+30).setChecked(True)
            self.illumination_btn_grp.button(
                self.illumination_list.index(self.header_list[self.current_index][7])+40).setChecked(True)
        else:
            for btn_grp in btn_grp_list:
                btn_grp.setExclusive(False)
                for btn in btn_grp.buttons():
                    btn.setChecked(False)
                btn_grp.setExclusive(True)

    def go_to_previous_image(self):
        self.current_index -= 1
        if self.current_index < 0: self.current_index = self.image_count - 1
        self.update_image_and_info()
        self.manage_checked_buttons()

    def go_to_next_image(self):
        self.current_index += 1
        if self.current_index >= self.image_count: self.current_index = 0
        self.update_image_and_info()
        self.manage_checked_buttons()

    def init_ui(self):
        self.configure_ui_elements()
        self.connect_buttons()

        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addLayout(self.create_folder_input_layout())
        layout.addLayout(self.create_metadata_status_layout())
        layout.addLayout(self.create_navigation_buttons_layout())
        layout.addStretch(1)
        layout.addLayout(self.create_image_and_checkboxes_layout())
        layout.addStretch(1)
        layout.addLayout(self.create_extra_button_layout())

        self.setLayout(layout)
        self.setWindowTitle('Image Metadata Annotator')
        self.resize(1000, 800)
        self.center_window()
        self.show()

    def configure_ui_elements(self):
        self.folder_input.setFixedWidth(350)
        self.integrity_check_btn.setEnabled(False)
        self.number_of_image_label.setAlignment(Qt.AlignCenter)

        self.previous_btn = QPushButton('<<< << < (A)', self)
        self.next_btn = QPushButton('(D) > >> >>>', self)
        self.recent_btn = QPushButton('Navigate to Most Recently Annotated Image', self)
        self.save_btn = QPushButton('Save Metadata (S)', self)
        self.extra_btn = QPushButton('Hello Out There', self)
        self.save_btn.setFixedWidth(180)

    def connect_buttons(self):
        self.folder_select_btn.clicked.connect(self.open_folder)
        self.save_btn.clicked.connect(self.save_metadata_to_csv)
        self.extra_btn.clicked.connect(self.show_extra_dialog)

        self.previous_btn.clicked.connect(self.go_to_previous_image)
        self.next_btn.clicked.connect(self.go_to_next_image)
        self.recent_btn.clicked.connect(self.navigate_to_recently_annotated_image)

    def create_folder_input_layout(self):
        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.folder_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.folder_input, alignment=Qt.AlignCenter)
        layout.addWidget(self.folder_select_btn, alignment=Qt.AlignCenter)
        layout.addStretch(1)
        return layout

    def create_metadata_status_layout(self):
        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.number_of_image_label, alignment=Qt.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(self.integrity_check_btn, alignment=Qt.AlignCenter)
        layout.addStretch(1)
        return layout

    def create_navigation_buttons_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(self.previous_btn, alignment=Qt.AlignCenter)
        layout.addWidget(self.next_btn, alignment=Qt.AlignCenter)
        layout.addWidget(self.file_num_name, alignment=Qt.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(self.recent_btn, alignment=Qt.AlignCenter)
        return layout

    def create_image_and_checkboxes_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(self.image_label)
        layout.addLayout(self.create_checkboxes_layout())
        return layout

    def create_checkboxes_layout(self):
        layout = QVBoxLayout()
        groups = [
            'Indoor / Outdoor',
            'Weather Conditions',
            'Time Stamp',
            'Motion Blur',
            'Illuminance'
        ]
        lists = [
            self.indoor_outdoor_list,
            self.weather_condition_list,
            self.time_of_day_list,
            self.motion_list,
            self.illumination_list
        ]
        btn_grps = [
            self.indoor_outdoor_btn_grp,
            self.weather_condition_btn_grp,
            self.time_of_day_btn_grp,
            self.motion_btn_grp,
            self.illumination_btn_grp
        ]
        widths = [100, 240, 160, 80, 110]

        for grp, list_, btn_grp, width in zip(groups, lists, btn_grps, widths):
            layout.addWidget(self.create_group(grp, list_, btn_grp, 180, width), alignment=Qt.AlignCenter)
        layout.addWidget(self.save_btn, alignment=Qt.AlignCenter)
        layout.addStretch(1)
        return layout

    def create_extra_button_layout(self):
        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.extra_btn, alignment=Qt.AlignCenter)
        layout.addStretch(1)
        return layout

    def center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def handle_key_press_event(self, e):
        if e.key() == Qt.Key_A: self.go_to_previous_image()
        if e.key() == Qt.Key_D: self.go_to_next_image()
        if e.key() == Qt.Key_S: self.save_metadata_to_csv()
        if e.key() == Qt.Key_E: self.navigate_to_recently_annotated_image()
        if e.key() == Qt.Key_Return: self.open_folder()


if __name__ == '__main__':
    viewer = QApplication(sys.argv)
    ex = Annotator()
    sys.exit(viewer.exec_())
