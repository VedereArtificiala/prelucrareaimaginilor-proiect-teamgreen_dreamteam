import cv2
import face_recognition
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

facesList = []
namesList = []

#info- se recomanda folosirea pozelor cu extensie .jpeg
def webcam(thisFrame):
    currentFrame = cv2.resize(thisFrame, (0, 0), fx=0.25, fy=0.25)
    faceLocations = face_recognition.face_locations(currentFrame, number_of_times_to_upsample=1, model='hog')

    faceEncodings = face_recognition.face_encodings(currentFrame, faceLocations)

    for faceLocation, faceEncoding in zip(faceLocations, faceEncodings):
        top, right, bottom, left = faceLocation

        top = top * 4
        right = right * 4
        bottom = bottom * 4
        left = left * 4

        faceMatches = face_recognition.compare_faces(facesList, np.array(faceEncoding))

        name = 'N/A'

        if True in faceMatches:
            firstMatchID = faceMatches.index(True)
            name = str(namesList[firstMatchID])

        cv2.rectangle(thisFrame, (left, top), (right, bottom), (255, 0, 0), 2)

        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(thisFrame, name, (left, bottom), font, 0.5, (255, 255, 255), 1)
    return thisFrame


def faceInfo(image):
    faceLocation = face_recognition.face_locations(np.array(image), number_of_times_to_upsample=2)[0]

    encode = face_recognition.face_encodings(image)[0]
    top, right, bottom, left = faceLocation
    cv2.rectangle(image, (right, bottom), (left, top), (0, 255, 255), 2)
    toReturn = (faceLocation, encode, image)

    return toReturn


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.saveWindow = saveFaceUI()
        facesList = []
        with open('data.txt', 'r+') as dataRead:
            lines = dataRead.readlines()
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
                facesList.append(a)
                name = name.split("{'name': '")[1].split("', 'face_location'")[0]
                namesList.append(name)

    def setupUI(self):
        if not self.objectName():
            self.setObjectName(u"MainWindow")

        self.resize(800, 540)
        self.setAutoFillBackground(True)

        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName(u"centralwidget")

        self.addFace = QPushButton(self.centralwidget)
        self.addFace.setObjectName(u"add_face_in_database")
        self.addFace.setGeometry(QRect(530, 220, 121, 30))
        self.addFace.setAutoFillBackground(True)

        self.startCam = QPushButton(self.centralwidget)
        self.startCam.setObjectName(u"start_camera_button")
        self.startCam.setGeometry(QRect(530, 175, 121, 30))
        self.startCam.setAutoFillBackground(True)

        self.cmdBoxText = QTextBrowser(self.centralwidget)
        self.cmdBoxText.setObjectName(u"command_box_text")
        self.cmdBoxText.setGeometry(QRect(530, 20, 256, 140))

        self.cameraLabel = QLabel(self.centralwidget)
        self.cameraLabel.setObjectName(u"camera_label")
        self.cameraLabel.setGeometry(QRect(20, 20, 500, 500))
        self.cameraLabel.setAutoFillBackground(True)
        self.cameraLabel.setFrameShape(QFrame.Box)
        self.cameraLabel.setFrameShadow(QFrame.Raised)
        self.cameraLabel.setMidLineWidth(4)

        self.setCentralWidget(self.centralwidget)

        self.setWindowTitle(QCoreApplication.translate("MainWindow", u"[PIM-P]Detecția și recunoașterea fețelor", None))
        self.addFace.setText(QCoreApplication.translate("MainWindow", u"Salvează o față", None))
        self.startCam.setText(QCoreApplication.translate("MainWindow", u"Pornește camera", None))
        self.startCamButton = 1 

        self.addFace.clicked.connect(self.addFaceButton)
        self.startCam.clicked.connect(self.startCameraButton)

        QMetaObject.connectSlotsByName(self)

    def addFaceButton(self):
        self.cmdBoxText.append('Debug - s-a apăsat butonul de salvare a unei fețe')
        if self.saveWindow.isVisible():
            self.saveWindow.hide()
        else:
            self.saveWindow.show()

    def startCameraButton(self):
        if self.startCamButton == 1:
            self.cmdBoxText.append('Debug - s-a apăsat butonul de pornire a camerei')
            self.startCam.setText(QCoreApplication.translate("MainWindow", u"Oprește camera", None))
            self.startCamButton = 0
            self.camThread = Thread()
            self.camThread.start()
            self.camThread.image_update.connect(self.imageUpdate)
        elif self.startCamButton == 0:
            self.cmdBoxText.append('Debug - s-a apăsat butonul de oprire a camerei')
            self.startCam.setText(QCoreApplication.translate("MainWindow", u"Pornește camera", None))
            self.startCamButton = 1
            self.camThread.stop()

    def imageUpdate(self, img):
        self.cameraLabel.setPixmap(QPixmap.fromImage(img))

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Confirmare',
                                     'Sigur vrei să închizi aplicația?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.startCamButton == 0:
                self.camThread.stop()
            event.accept()
        else:
            event.ignore()


class Thread(QThread):
    image_update = pyqtSignal(QImage)

    def run(self) -> None:
        self.isThreadActive = True
        cameraCapture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cameraCapture.set(cv2.CAP_PROP_FRAME_WIDTH, 500)
        cameraCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

        while self.isThreadActive:
            ret, thisFrame = cameraCapture.read()
            if ret:
                thisFrame = cv2.cvtColor(thisFrame, cv2.COLOR_BGR2RGB)
                thisFrame = webcam(thisFrame)
                current_frame_converted_to_qt = QImage(thisFrame.data, thisFrame.shape[1],
                                                       thisFrame.shape[0], QImage.Format_RGB888)
                current_frame_converted_to_qt = current_frame_converted_to_qt.scaled(500, 500, Qt.KeepAspectRatio)
                self.image_update.emit(current_frame_converted_to_qt)
        cameraCapture.release()

    def stop(self):
        self.isThreadActive = False
        self.quit()


class saveFaceUI(QtWidgets.QDialog):
    def __init__(self):
        self.name = ''
        self.image = None
        self.faceEncode = None
        self.faceLocation = None

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

        self.browseBtn = QPushButton(self)
        self.browseBtn.setObjectName(u"browse_button")
        self.browseBtn.setGeometry(QRect(550, 300, 120, 30))

        self.saveBtn = QPushButton(self)
        self.saveBtn.setObjectName(u"save_button")
        self.saveBtn.setGeometry(QRect(550, 340, 120, 30))

        self.dataFromTxt = QTextBrowser(self)
        self.dataFromTxt.setObjectName(u"textBrowser")
        self.dataFromTxt.setGeometry(QRect(550, 20, 200, 200))
        self.dataFromTxt.append('Saved data:')
        with open('data.txt', 'r') as data_to_read:
            lines = data_to_read.readlines()
            for line in lines:
                line = line.split("{'name': '")[1].split("'")[0]
                self.dataFromTxt.append('Name: ' + line)

        self.cmdBoxTxt = QTextBrowser(self)
        self.cmdBoxTxt.setObjectName(u"command_box_text")
        self.cmdBoxTxt.setGeometry(QRect(550, 400, 200, 120))

        self.faceName = QLineEdit(self)
        self.faceName.setObjectName(u"face_name")
        self.faceName.setGeometry(QRect(550, 260, 200, 30))

        self.setWindowTitle(QCoreApplication.translate("SecondWindow", u"Salvare fețe in baza de date", None))
        self.browseBtn.setText(QCoreApplication.translate("SecondWindow", u"Caută", None))
        self.saveBtn.setText(QCoreApplication.translate("SecondWindow", u"Salvează", None))
        self.label.setText("")

        self.browseBtn.clicked.connect(self.browseButton)
        self.saveBtn.clicked.connect(self.saveButton)

        QMetaObject.connectSlotsByName(self)

    def saveButton(self):
        self.cmdBoxTxt.append('Debug - s-a apăsat butonul de salvare a unei fețe')
        self.name = self.faceName.text()
        if (self.name != '')\
                and (self.faceLocation is not None) \
                and (self.faceEncode is not None):
            data_to_save = {
                'name': self.name,
                'face_location': self.faceLocation,
                'face_encode': self.faceEncode
            }
            with open('data.txt', 'a') as data_file:
                data_file.write(str(data_to_save) + '\n')
        else:
            self.cmdBoxTxt.append('Înainte de a salva, te rog introdu numele')

    def browseButton(self):
        self.cmdBoxTxt.append('Browse for image button clicked.')
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 'C:/Users/selim/Desktop/prelucrareaimaginilor-proiect-teamgreen_dreamteam-main/Images', '*.jpeg')
        if not(fileName == ''):
            self.image = cv2.imread(fileName)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            image_data = faceInfo(self.image)
            self.faceLocation = image_data[0]  
            self.faceEncode = (str(image_data[1])) 
            self.image = image_data[2] 
            image_to_qt = QImage(self.image.data, self.image.shape[1], self.image.shape[0], QImage.Format_RGB888)
            self.label.setPixmap(QPixmap(image_to_qt.scaled(500, 500, Qt.KeepAspectRatio)))
        else:
            pass
