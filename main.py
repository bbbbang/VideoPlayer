import sys
from PyQt5.QtGui import QImage, QPixmap, QStandardItem, QStandardItemModel, QBrush, QColor
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QModelIndex, QThread, pyqtSlot
import cv2
import threading
import glob
import os
from time import sleep
import io
import folium
from PyQt5 import QtWidgets, QtWebEngineWidgets

playing = False

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'qt'
        self.left = 100
        self.top = 100
        self.width = 1000
        self.height = 700
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
 
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)
 
        self.show()
 
 
class MyTableWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # 탭 스크린 설정
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tabs.resize(300, 200)
 
        # 탭 추가
        self.tabs.addTab(self.tab1, "Tab 1")
        self.tabs.addTab(self.tab2, "Tab 2")
        self.tabs.addTab(self.tab3, "Tab 3")

 
        # 첫번째 탭 레이아웃 설정
        self.tab1.layout = QVBoxLayout(self)
        self.pushButton1 = QPushButton("PyQt5 button")
        self.pushButton1.clicked.connect(self.OpenFile)
    
        self.label = QLabel()

        self.tab1.layout.addWidget(self.pushButton1)
        self.tab1.layout.addWidget(self.label)
        self.tab1.setLayout(self.tab1.layout)
 
        # 두번째 탭 레이아웃 설정
        # self.tab2.layout = QVBoxLayout(self)
        self.tab2.layout = QGridLayout(self)
        self.listView = QListView(self)
        self.model = QStandardItemModel()

        items = ['as', 'as', 'df', 'bv', 'zx', 'asd', 'erw', 'rrr', 'www', 'qwf', 'gdfb', 'zxc', 'eter']
        for f in items:
            self.model.appendRow(QStandardItem(f))
        self.listView.setModel(self.model)
        self.tab2.layout.addWidget(self.listView, 0, 0)

        self.locList = []
        self.locX = 37.564214
        self.locY = 127.001699
        loc = [self.locX, self.locY]
        self.locList.append(loc)
        m = folium.Map(location=[self.locX, self.locY], tiles="OpenStreetMap", zoom_start=15)
        
        data = io.BytesIO()
        m.save(data, close_file=False)
        
        self.w = QtWebEngineWidgets.QWebEngineView()
        self.w.setHtml(data.getvalue().decode())

        self.tab2.layout.addWidget(self.w, 0, 1)

        self.pushButton2 = QPushButton("PyQt5 button")
        self.tab2.layout.addWidget(self.pushButton2, 1, 0)

        self.pushButton3 = QPushButton("PyQt4444445 button")
        self.pushButton3.clicked.connect(self.test)
        self.tab2.layout.addWidget(self.pushButton3, 1, 1)

        self.tab2.setLayout(self.tab2.layout)
 
        self.tab3.layout = QVBoxLayout(self)
        self.table_widget = VideoManager(self)
        self.tab3.layout.addWidget(self.table_widget)
        self.tab3.setLayout(self.tab3.layout)

        # 그리고 위젯에 탭 추가
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
 
    def OpenFile(self):
        fname = QFileDialog.getOpenFileName(self)
        self.label.setText(fname[0])

    def test(self):
        self.locX += 0.00333
        self.locY += 0.00333
        loc = [self.locX, self.locY]
        self.locList.append(loc)
        m = folium.Map(location=[self.locX, self.locY], tiles="OpenStreetMap", zoom_start=15)
        
        for l in self.locList:
            folium.Marker(location=[l[0], l[1]], icon=folium.Icon(color='red', icon='star'), popup="Center of seoul").add_to(m)
        data = io.BytesIO()
        m.save(data, close_file=False)
        
        self.w.setHtml(data.getvalue().decode())

class VideoManager(QWidget):
    videoName = ''
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        self.open = QPushButton('Open Video')
        self.open.clicked.connect(self.OpenFile)

        self.start = QPushButton('START')
        self.start.clicked.connect(self.Start)

        self.stop = QPushButton('STOP')
        self.stop.clicked.connect(self.Stop)

        self.label = QLabel()

        self.listView = QListView(self)
        self.model = QStandardItemModel()
        self.listView.doubleClicked[QModelIndex].connect(self.onClick)
        #items = ['as', 'as', 'df', 'bv', 'zx', 'asd', 'erw', 'rrr', 'www', 'qwf', 'gdfb', 'zxc', 'eter']
        #for f in items:
        #    self.model.appendRow(QStandardItem(f))
        self.listView.setModel(self.model)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tt = QLabel()
        self.layout.addWidget(self.tt)
        self.layout.addWidget(self.listView)

        self.layout.addWidget(self.open)
        self.layout.addWidget(self.start)
        self.layout.addWidget(self.stop)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def onClick(self, index):
        item = self.model.itemFromIndex(index)
        self.tt.setText("on_clicked: itemIndex=`{}`, itemText=`{}`"
                           "".format(item.index().row(), item.text()))
        item.setForeground(QBrush(QColor(255, 0, 0))) 
        self.itemOld.setForeground(QBrush(QColor(0, 0, 0))) 
        self.itemOld = item

    def OpenFile(self):
        global videoName
        fname = QFileDialog.getOpenFileName(self)
        videoName = fname[0]
        s = os.path.split(videoName)
        self.videoList = glob.glob(s[0] + '/*.mp4')
        print(self.videoList)

        for f in self.videoList:
            self.model.appendRow(QStandardItem(f))

        self.cap = cv2.VideoCapture(videoName)
        self.itemOld = QStandardItem("text")


    def Play(self):
        global playing
        # global videoName
        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.label.resize(width, height)

        while 1:
            if playing:
                ret, img = self.cap.read()

                if ret:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
                    h,w,c = img.shape
                    qImg = QImage(img.data, w, h, w*c, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qImg)
                    self.label.setPixmap(pixmap)
                    self.label.update()
                    sleep(0.03)
                else:
                    self.cap.release()
                    print("Thread end.")
                    break


    def Start(self):
        global playing
        playing = True
        self.th = threading.Thread(target=self.Play)
        self.th.start()
        print("started..")

    def Stop(self):
        global playing

        if playing == True:
            playing = False
            print("stoped..")
        else:
            playing = True
            print("started..")
 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())