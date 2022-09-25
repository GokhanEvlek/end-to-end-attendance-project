from PyQt5 import QtWidgets
import sys
from hui_form import Ui_MainWindow


import cv2 as cv

from PyQt5.QtGui import QPixmap

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from dis import dis
import cv2 as cv

import time
import numpy as np

from deepface.commons import distance as dst
from deepface.DeepFace import *


from deepface.basemodels import Facenet

import mysql.connector 
import json
import csv




Capture = cv.VideoCapture(0)
model_name='Facenet'
distance_metric='euclidean'

enforce_detection = True
detector_backend = 'mtcnn'
align = True
prog_bar = True 

normalization = 'base'
blank_foto= cv.imread("images.jpg")


blank_foto = cv.resize(blank_foto, (112,112))

model = build_model(model_name)
frame=cv.imread("images.jpg")


csvyeyazildi=0
kayityapildi=0
kayityapiliyor=0
basligiyaz=1

class myApp(QtWidgets.QMainWindow):

    def __init__(self):
        super(myApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)












        self.ui.stackedWidget.setCurrentWidget(self.ui.secim_ekrani)
        self.ui.ogrenci_ekleme.clicked.connect(self.ogrencikaydi)
        self.ui.yoklama_alma.clicked.connect(self.yoklama)
        self.ui.anamenuyedonus.clicked.connect(self.anamenu)

    def ogrencikaydi(self):

        self.ui.stackedWidget.setCurrentWidget(self.ui.kayit_ekrani)
        print("yuz tanima basladı")
        self.Worker1 = Worker1()
        self.Worker1.start()
        self.ui.anamenuyedonus.clicked.connect(self.CancelFeed)
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)


    def yoklama(self):
        
        self.ui.stackedWidget.setCurrentWidget(self.ui.yoklama)
        self.Worker2 = Worker2()
        self.Worker2.start()
        self.ui.anamenuyedonus.clicked.connect(self.CancelFeed2)

        self.Worker2.ImageUpdate2.connect(self.ImageUpdateSlot2)




    def anamenu(self):

        self.ui.stackedWidget.setCurrentWidget(self.ui.secim_ekrani)



    def ImageUpdateSlot(self, Image,kafa):
        global csvyeyazildi
        #self.ui.fototutucu.setPixmap(QPixmap.fromImage(Image))
        pixmap = QPixmap("foto.jpg")
        self.ui.kafatutucu.setPixmap(QPixmap.fromImage(kafa))
        #self.ui.veritabanfoto.setPixmap(pixmap)
        self.ui.fototutucu.setPixmap(QPixmap.fromImage(Image))
        #self.ui.kafatutucu_base.setPixmap(QPixmap.fromImage(kafa_base))
        if csvyeyazildi==1:
            self.ui.ogrencieklendi.setText('Ogrenci kaydedildi')
            self.ui.ogrencieklenemedi.setText('')
            
            


            loop = QEventLoop()
            QTimer.singleShot(2000, loop.quit)
            loop.exec_()
            csvyeyazildi=0


        if csvyeyazildi==2:
            self.ui.ogrencieklenemedi.setText('Ogrenci Zaten Kayıtlı')
            self.ui.ogrencieklendi.setText('')
            csvyeyazildi=0
        else :
            self.ui.ogrencieklenemedi.setText('Ogrenci Tespit Edilmedi')
            self.ui.ogrencieklendi.setText('')
            loop = QEventLoop()
            QTimer.singleShot(2000, loop.quit)
            loop.exec_()
            csvyeyazildi=0
            




    def kayit(self):
        global frame,kayityapiliyor
        kayityapiliyor=1
        try:
            
            img2_representation,detected_face = represent(img_path = frame
            , model_name = model_name, model = model
            , enforce_detection = enforce_detection, detector_backend = detector_backend
            , align = align
            , normalization = normalization
            )
            jsonStr = json.dumps(img2_representation)
            ad=self.ui.ogrenciad.text()
            soyad=self.ui.Ogrencisoyad.text()
            no=int(self.ui.ogrencino.text())
            connection = mysql.connector.connect(host='localhost',
                                        database='deneme',
                                        user='root',
                                        password='1234')
            cursor = connection.cursor()


            mySql_insert_query = "INSERT INTO ogrenci (idogrenci, ograd, ogrsoyad, embedding) VALUES ("+str(no)+","+"'"+ad+"', '"+soyad+"', '"+jsonStr+ "') "
            print(mySql_insert_query)



            try:
                cursor.execute(mySql_insert_query)
                connection.commit()
                print(cursor.rowcount, "Record inserted successfully into Laptop table")
                cursor.close()
                self.ui.kayit_tamamlandi.setText('Öğrenci Kaydı Tamamlandı')
                
                loop = QEventLoop()
                QTimer.singleShot(4000, loop.quit)
                loop.exec_()
                
            except:
                self.ui.kayit_tamamlandi.setText('Öğrenci Zaten Kayıtlı')
        except:
            print("Yuz bulunamadi ")
            self.ui.kayit_tamamlandi.setText('Öğrenci Yüzü Tespit Edilemedi')
        kayityapiliyor=0        
        self.ui.ogrenci_kaydet.disconnect()
    
    def ImageUpdateSlot2(self, Image):
        global frame

        self.ui.ogrencifoto.setPixmap(QPixmap.fromImage(Image))
        self.ui.ogrenci_kaydet.clicked.connect(self.kayit)
        
        

    def CancelFeed(self):
        self.Worker1.stop()

    def CancelFeed2(self):
        self.Worker2.stop()



class Worker2(QThread):
    ImageUpdate2 = pyqtSignal(QImage)
    

    def run(self):

        global Capture,model_name,model,enforce_detection,detector_backend,align,normalization,blank_foto,frame,kayityapiliyor

        self.ThreadActive = True
        
        
 
        connection = mysql.connector.connect(host='localhost',
                                         database='deneme',
                                         user='root',
                                         password='1234')

        




        while self.ThreadActive:

                ret, frame = Capture.read()
                if ret:
            

                    dim = (480, 640)


                    frame_ogrenci = cv.cvtColor(frame, cv.COLOR_BGR2RGB)                
                    frame_ogrenci = cv.resize(frame_ogrenci,dim,interpolation = cv.INTER_AREA)          
                    
                    frame_ogrenci = cv.flip(frame_ogrenci, 1)
                    frame_ogrenci = QImage(frame_ogrenci.data, frame_ogrenci.shape[1], frame_ogrenci.shape[0], QImage.Format_RGB888)
                    #Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                    if kayityapiliyor==0:
                        self.ImageUpdate2.emit(frame_ogrenci)
    def stop(self):
        self.ThreadActive = False
        self.quit()


class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage,QImage)


    def run(self):

        global Capture,model_name,model,enforce_detection,detector_backend,align,normalization,blank_foto,csvyeyazildi

        self.ThreadActive = True
        
        yazilmali=1


        """
        img_base = cv.imread("C:\\WhatsAppImage2022-09-1920.23.10.jpeg")
        img1_representation,detected_face_base = represent(img_path = img_base
            , model_name = model_name, model = model
            , enforce_detection = enforce_detection, detector_backend = detector_backend
            , align = align
            , normalization = normalization
            )
        detected_face_base= cv.cvtColor(detected_face_base, cv.COLOR_BGR2RGB)
        
        print(type(img1_representation))
        jsonStr = json.dumps(img1_representation)
        print(type(jsonStr))
        print(jsonStr)
        """
        connection = mysql.connector.connect(host='localhost',
                                         database='deneme',
                                         user='root',
                                         password='1234')

        
        sql_select_Query = "select * from ogrenci"
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        # get all records
        records = cursor.fetchall()
        print("Total number of rows in table: ", cursor.rowcount)
        print(type(records[0][3]))
        base_embedding=json.loads(records[0][3])
        print(type(base_embedding))
        """
        cursor = connection.cursor()
        mySql_insert_query = "INSERT INTO ogrenci (idogrenci, ograd, ogrsoyad, embedding) VALUES (109,'Gokhan','Evlek', '"+jsonStr+ "') "
        cursor.execute(mySql_insert_query)
        connection.commit()
        print(cursor.rowcount, "Record inserted successfully into Laptop table")
        cursor.close()
        """

        while self.ThreadActive:
            ret, frame = Capture.read()
            if ret:
                
                try:
                    img2_representation,detected_face = represent(img_path = frame
                    , model_name = model_name, model = model
                    , enforce_detection = enforce_detection, detector_backend = detector_backend
                    , align = align
                    , normalization = normalization
                    )
                    for row in records:
                        base_embedding=json.loads(row[3])
                        distance = dst.findEuclideanDistance(base_embedding, img2_representation)
                        distance = np.float64(distance)




                        if distance<10:
                            print("Eslesme oldu: ",distance)
                            with open('students.csv', 'r',newline='') as file:
                                csvreader = csv.reader(file)
                                header = next(csvreader)
                                for row_csv in csvreader:
                                    print("csv den gelen: ",row_csv)
                                    print("veri tabanından gelen: ", row[0:3])
                                    if len(row_csv)==0:
                                        continue
                                    print(type(row))
                                    print(type(row_csv))
                                    print(type(row_csv[0]))
                                    if str(row_csv[0])==str(row[0]) and row_csv[1]==row[1] and row_csv[2]==row[2]:
                                        yazilmali=0
                                        csvyeyazildi=2



                            if yazilmali==1:
                                with open('students.csv', 'a',newline='') as file:
                                    writer = csv.writer(file)
                                    student_data=[row[0],row[1],row[2]]

                                    writer.writerow(student_data)
                                    csvyeyazildi=1

                            else:
                                yazilmali=1


                except:
                    print("Yuz bulunamadi ")
                    detected_face=blank_foto

                dim = (480, 640)
                dim2= (64,64)


                """
                detected_face_base = cv.resize(detected_face_base,dim2,interpolation = cv.INTER_AREA)
                flippedkafa_base=cv.flip(detected_face_base,1)
                ConvertToQtFormatkafa_base = QImage(flippedkafa_base.data, flippedkafa_base.shape[1], flippedkafa_base.shape[0], QImage.Format_RGB888)
                """

                detected_face = cv.cvtColor(detected_face, cv.COLOR_BGR2RGB)   
                detected_face = cv.resize(detected_face,dim2,interpolation = cv.INTER_AREA)
                flippedkafa=cv.flip(detected_face,1)
                ConvertToQtFormatkafa = QImage(flippedkafa.data, flippedkafa.shape[1], flippedkafa.shape[0], QImage.Format_RGB888)
                
                frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)                
                frame = cv.resize(frame,dim,interpolation = cv.INTER_AREA)          
                
                FlippedImage = cv.flip(frame, 1)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                #Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(ConvertToQtFormat,ConvertToQtFormatkafa)
    def stop(self):
        self.ThreadActive = False
        self.quit()



















def app():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("QPushButton { color: red}")
    win = myApp()
    win.show()
    sys.exit(app.exec_())

student_header = ['StudentId', 'Name', 'Surname']
if basligiyaz==1:
    with open('students.csv', 'a') as file:
        pass
    
with open('students.csv', 'r',newline='') as file:
    csvreader = csv.reader(file)
    for row_csv in csvreader:
        print("csv den gelen: ",row_csv)
        if len(row_csv)==0:
            continue
        if str(row_csv[0])==str(student_header[0]) and row_csv[1]==student_header[1] and row_csv[2]==student_header[2]:
            basligiyaz=0

if basligiyaz==1:
    with open('students.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow(student_header)

app()
