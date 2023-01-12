import cv2
import face_recognition
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

faces_list = []
name_list = []

def webcam(current_frame):
    current_frame_small = cv2.resize(current_frame, (0, 0), fx=0.25, fy=0.25)
    all_face_locations = face_recognition.face_locations(current_frame_small, number_of_times_to_upsample=1, model='hog')

    all_face_encodings = face_recognition.face_encodings(current_frame_small, all_face_locations)

    for current_face_location, current_face_encoding in zip(all_face_locations, all_face_encodings):
        top_pos, right_pos, bottom_pos, left_pos = current_face_location

        top_pos = top_pos * 4
        right_pos = right_pos * 4
        bottom_pos = bottom_pos * 4
        left_pos = left_pos * 4

        all_matches = face_recognition.compare_faces(faces_list, np.array(current_face_encoding))

        name_of_person = 'Unknown face'

        if True in all_matches:
            first_match_index = all_matches.index(True)
            name_of_person = str(name_list[first_match_index])

        cv2.rectangle(current_frame, (left_pos, top_pos), (right_pos, bottom_pos), (255, 0, 0), 2)

        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(current_frame, name_of_person, (left_pos, bottom_pos), font, 0.5, (255, 255, 255), 1)
    return current_frame


def faceInfo(image):
    face_location = face_recognition.face_locations(np.array(image), number_of_times_to_upsample=2)[0]

    encode_image = face_recognition.face_encodings(image)[0]
    top_pos, right_pos, bottom_pos, left_pos = face_location
    cv2.rectangle(image, (right_pos, bottom_pos), (left_pos, top_pos), (0, 255, 255), 2)
    return_tuple = (face_location, encode_image, image)

    return return_tuple


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.save_face_window = saveFaceUI()
        faces_list = []
        with open('Python_files/data.txt', 'r+') as data_to_read:
            lines = data_to_read.readlines()
            for line in lines:
                s = ''
                name = line
                line = line.split("'face_encode'")[1][2:].split("'")[1]
                s += line[0]
                for i in range(1, len(line)):
                    if line[i - 1] == '\\' and line[i] == 'n':
                        s += '\n'
                    else:
                        s += line[i]
                s = s.replace('\\', '')
                a = np.fromstring(s)
                faces_list.append(a)
                name = name.split("{'name': '")[1].split("', 'face_location'")[0]
                name_list.append(name)

    def setupUI(self):
        if not self.objectName():
            self.setObjectName(u"MainWindow")

        self.resize(800, 540)
        self.setAutoFillBackground(True)

        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName(u"centralwidget")

        self.add_face_in_database = QPushButton(self.centralwidget)
        self.add_face_in_database.setObjectName(u"add_face_in_database")
        self.add_face_in_database.setGeometry(QRect(530, 220, 121, 30))
        self.add_face_in_database.setAutoFillBackground(True)

        self.start_camera_button = QPushButton(self.centralwidget)
        self.start_camera_button.setObjectName(u"start_camera_button")
        self.start_camera_button.setGeometry(QRect(530, 175, 121, 30))
        self.start_camera_button.setAutoFillBackground(True)

        self.command_box_text = QTextBrowser(self.centralwidget)
        self.command_box_text.setObjectName(u"command_box_text")
        self.command_box_text.setGeometry(QRect(530, 20, 256, 140))

        self.camera_label = QLabel(self.centralwidget)
        self.camera_label.setObjectName(u"camera_label")
        self.camera_label.setGeometry(QRect(20, 20, 500, 500))
        self.camera_label.setAutoFillBackground(True)
        self.camera_label.setFrameShape(QFrame.Box)
        self.camera_label.setFrameShadow(QFrame.Raised)
        self.camera_label.setMidLineWidth(4)

        self.setCentralWidget(self.centralwidget)

        self.setWindowTitle(QCoreApplication.translate("MainWindow", u"Face recognition project", None))
        self.add_face_in_database.setText(QCoreApplication.translate("MainWindow", u"Save a face in DB", None))
        self.start_camera_button.setText(QCoreApplication.translate("MainWindow", u"Start camera", None))
        self.start_camera_button_control = 1 

        self.add_face_in_database.clicked.connect(self.addFaceButton)
        self.start_camera_button.clicked.connect(self.startCameraButton)

        QMetaObject.connectSlotsByName(self)

    def addFaceButton(self):
        self.command_box_text.append('Add a face in database button clicked.')
        if self.save_face_window.isVisible():
            self.save_face_window.hide()
        else:
            self.save_face_window.show()

    def startCameraButton(self):
        if self.start_camera_button_control == 1:
            self.command_box_text.append('Start camera button clicked.')
            self.start_camera_button.setText(QCoreApplication.translate("MainWindow", u"Stop camera", None))
            self.start_camera_button_control = 0
            self.camera_thread = Thread()
            self.camera_thread.start()
            self.camera_thread.image_update.connect(self.imageUpdate)
        elif self.start_camera_button_control == 0:
            self.command_box_text.append('Stop camera button clicked.')
            self.start_camera_button.setText(QCoreApplication.translate("MainWindow", u"Start camera", None))
            self.start_camera_button_control = 1
            self.camera_thread.stop()

    def imageUpdate(self, img):
        self.camera_label.setPixmap(QPixmap.fromImage(img))

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Quit?',
                                     'Are you sure you want to quit?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.start_camera_button_control == 0:
                self.camera_thread.stop()
            event.accept()
        else:
            event.ignore()


class Thread(QThread):
    image_update = pyqtSignal(QImage)

    def run(self) -> None:
        self.thread_active = True
        webcam_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        webcam_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 500)
        webcam_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

        while self.thread_active:
            ret, current_frame = webcam_capture.read()
            if ret:
                current_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
                current_frame = webcam(current_frame)
                current_frame_converted_to_qt = QImage(current_frame.data, current_frame.shape[1],
                                                       current_frame.shape[0], QImage.Format_RGB888)
                current_frame_converted_to_qt = current_frame_converted_to_qt.scaled(500, 500, Qt.KeepAspectRatio)
                self.image_update.emit(current_frame_converted_to_qt)
        webcam_capture.release()

    def stop(self):
        self.thread_active = False
        self.quit()


class saveFaceUI(QtWidgets.QDialog):
    def __init__(self):
        self.name = ''
        self.image = None
        self.face_encode = None
        self.face_location = None

        super().__init__()
        self.setObjectName(u"SecondWindow")
        self.resize(800, 550)

        self.label = QLabel(self)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(30, 20, 500, 500))
        self.label.setFrameShape(QFrame.Panel)
        self.label.setFrameShadow(QFrame.Raised)
        self.label.setMidLineWidth(4)
        self.label.setScaledContents(False)

        self.browse_button = QPushButton(self)
        self.browse_button.setObjectName(u"browse_button")
        self.browse_button.setGeometry(QRect(550, 300, 120, 30))

        self.save_button = QPushButton(self)
        self.save_button.setObjectName(u"save_button")
        self.save_button.setGeometry(QRect(550, 340, 120, 30))

        self.data_in_database = QTextBrowser(self)
        self.data_in_database.setObjectName(u"textBrowser")
        self.data_in_database.setGeometry(QRect(550, 20, 200, 200))
        self.data_in_database.append('Saved data:')
        with open('Python_files/data.txt', 'r') as data_to_read:
            lines = data_to_read.readlines()
            for line in lines:
                line = line.split("{'name': '")[1].split("'")[0]
                self.data_in_database.append('Name: ' + line)

        self.command_box_text = QTextBrowser(self)
        self.command_box_text.setObjectName(u"command_box_text")
        self.command_box_text.setGeometry(QRect(550, 400, 200, 120))

        self.face_name = QLineEdit(self)
        self.face_name.setObjectName(u"face_name")
        self.face_name.setGeometry(QRect(550, 260, 200, 30))

        self.setWindowTitle(QCoreApplication.translate("SecondWindow", u"Form", None))
        self.browse_button.setText(QCoreApplication.translate("SecondWindow", u"Browse for image", None))
        self.save_button.setText(QCoreApplication.translate("SecondWindow", u"Save in database", None))
        self.label.setText("")

        self.browse_button.clicked.connect(self.browseButton)
        self.save_button.clicked.connect(self.saveButton)

        QMetaObject.connectSlotsByName(self)

    def saveButton(self):
        self.command_box_text.append('Save in database button clicked.')
        self.name = self.face_name.text()
        if (self.name != '')\
                and (self.face_location is not None) \
                and (self.face_encode is not None):
            data_to_save = {
                'name': self.name,
                'face_location': self.face_location,
                'face_encode': self.face_encode
            }
            with open('Python_files/data.txt', 'a') as data_file:
                data_file.write(str(data_to_save) + '\n')
        else:
            self.command_box_text.append('Before saving, please enter the name or the image.')

    def browseButton(self):
        self.command_box_text.append('Browse for image button clicked.')
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 'C:/Users/emanu/Desktop/Proeict_PI'
                                                                                '/FaceRecognition/Images', '*.jpeg')
        if not(file_name == ''):
            self.image = cv2.imread(file_name)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            image_data = faceInfo(self.image)
            self.face_location = image_data[0]  
            self.face_encode = (str(image_data[1])) 
            self.image = image_data[2] 
            image_to_qt = QImage(self.image.data, self.image.shape[1], self.image.shape[0], QImage.Format_RGB888)
            self.label.setPixmap(QPixmap(image_to_qt.scaled(500, 500, Qt.KeepAspectRatio)))
        else:
            pass
