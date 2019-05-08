
""" GNR602 Course Project work

Title: Implementation of Canny Edge Detector

Submitted by
    Narayana Rao Bhogapurapu 184310003
    Vikram Kumar Purbey      183310014
    Gyaneshwar Patle         183310022
"""
import sys
import numpy as np
import cv2
from os import path
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtWidgets import QMessageBox,QLabel
import math
import time
### External files
import Threshold
import Hist_window
import sigma_in
from outplot_pyqt_tab import MplCanvas as mplt_plot

class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle("Canny Edge Detector")
        self.menu()
        self.center()
        self.statusBar()
        self.progress = QtWidgets.QProgressBar()
        self.statusBar().addPermanentWidget(self.progress)
        self.progress.setFixedSize(250,25)
        self.statusBar().showMessage('Ready')
        self.tab_Var = None
        self.completed = 0
        # Variables
        self.f_type = None
        self.t_index  = None
        self.raw_data = None
        self.grad = None
        self.gauss = None
        self.ang = None
        self.nonmax = None
        self.hys = None
        self.h_thres = None# Value
        self.l_thres = None# Value
        self.sthres = None# Data
        self.tthres = None# data
        self.sigma = None
        self.currentp = None
        self.imagefinal = None
        self.c_edge_image = None
        self.l_h_t = None
        self.gaussian_out  = None
        self.image_out_grad  = None
        self.image_out_angle  = None
        self.nonmaxima_img  = None
        self.threshold  = None
        self.strong = None
        self.windows_size = None
        self.image_final  = None
        self.threshold  = None

##############################################################################         
    def menu(self):
        """""""""""""""
        Tab Widget for Plotting
        """""""""""""""
        self.main_widget = QtWidgets.QWidget(self)
        self.gridLayout = QtWidgets.QGridLayout(self.main_widget)
        self.tabWidget = QtWidgets.QTabWidget(self.main_widget)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.gridLayout.addWidget(self.tabWidget)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)  
        self.tabWidget.tabCloseRequested.connect(self.close_tab)
        self.tab = QtWidgets.QWidget()    
        """""""""""""""
        Main Menu 
        """""""""""""""
#        '''File Menu'''
        File_open = QtWidgets.QAction("Open", self)
        File_open.setShortcut("Ctrl+O")
        File_open.setStatusTip('Open a File')
        File_open.triggered.connect(self.File_Open_window)
#        '''Process Menu'''
        c_edge = QtWidgets.QAction("Canny Edge Detector", self)
        c_edge.triggered.connect(self.G_Blur)                
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(File_open)
        processMenu = mainMenu.addMenu('&Process')
        processMenu.addAction(c_edge)
###############################################################################
        '''Main menu Callback Functions''' 
############################################################################### 
    def close_tab(self,index):
        self.tabWidget.removeTab(index)
    def add_tab(self):
        tab =QtWidgets.QWidget(self.tabWidget)
        self.tabWidget.addTab(tab,'Title')
        
        ''' Main Window Alighnment and Style'''              
    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def File_Open_window(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Image File',
                                                          filter=
                                                          "JPEG (*.jpg);;PNG(*.png);;All (*)")
        if file_name[0]:
            self.fname = file_name[0]
            self.f_type = path.splitext(file_name[0])
            (self.directory, self.filename) = path.split(self.fname)
            self.raw_data =np.array(cv2.imread(self.fname,cv2.IMREAD_GRAYSCALE))          
            self.tab_Var = mplt_plot(self.tab,self.raw_data)
            self.t_index = self.tabWidget.addTab(self.tab_Var, str(self.filename))
            self.tabWidget.setCurrentIndex(self.t_index)
        elif self.raw_data is None:
            self.infile_error()    
           
    def G_Blur(self):
        if self.raw_data is None:
            self.infile_error()
        else:
            
            input_dialog = QtWidgets.QDialog()
            input_ui3 = sigma_in.Ui_Dialog()
            input_ui3.setupUi(input_dialog)
            input_dialog.show()
            if input_dialog.exec():
                self.sigma = input_ui3.onOk()           
                ws = int(np.round(3 * self.sigma));
                shape = (ws,ws)
                m,n = [(ss-1.)/2. for ss in shape]
                y,x = np.ogrid[-m:m+1,-n:n+1]
                h = np.exp( -(x*x + y*y) / (2.*self.sigma*self.sigma) )
                h[ h < np.finfo(h.dtype).eps*h.max() ] = 0
                sumh = h.sum()
                if sumh != 0:
                    h /= sumh                                       
                fil=np.array(h)          
                gaussian_out = np.array(self.raw_data.copy())
                (h,w) = self.raw_data.shape
                (hf,wf)=fil.shape
                hf2=hf//2
                wf2=wf//2
                for i in range(hf2, h-hf2):
                  for j in range(wf2, w-wf2):
                    tsum=0
                    for ii in range(hf):
                        for jj in range(wf):
                            tsum=tsum+(self.raw_data[i-hf2+ii,j-wf2+jj]*fil[hf-1-ii,wf-1-jj])
                    gaussian_out[i][j]=tsum
                  if self.completed < 10:
                      self.completed += 0.1
                      self.progress.setValue(self.completed)
                self.gaussian_out = gaussian_out
                self.progress.setValue(self.completed)
                tab_Var = mplt_plot(self.tab,gaussian_out)
                self.t_index = self.tabWidget.addTab(tab_Var, 'Gaussian Blur')
                self.tabWidget.setCurrentIndex(self.t_index)
                QMessageBox.about(self,"Status!", "Gaussian Blur Applied!")
                self.gradient()          

    def gradient(self):
        image_out_grad = np.array(self.gaussian_out.copy())
        image_out_angle = np.array(self.gaussian_out.copy())
        gx=np.array([[-1,0,1],[-2,0,2],[-1,0,1]])
        gy=gx.T
    
        (h,w) = self.gaussian_out.shape
        (hf,wf)=gx.shape
       
        hf2=hf//2
        wf2=wf//2
        
        for i in range(hf2, h-hf2):
          for j in range(wf2, w-wf2):
            tsumx=0
            tsumy=0
            for ii in range(hf):
                for jj in range(wf):
                    tsumx=tsumx+(self.gaussian_out[i-hf2+ii,j-wf2+jj]*gx[hf-1-ii,wf-1-jj])
                    tsumy=tsumy+(self.gaussian_out[i-hf2+ii,j-wf2+jj]*gy[hf-1-ii,wf-1-jj])
            image_out_grad[i][j]=math.sqrt((tsumx*tsumx)+(tsumy*tsumy))
            theta = np.arctan2(tsumy, tsumx)
            image_out_angle[i][j] = (np.round(theta * (5.0 / np.pi)) + 5) % 5   #angle quantization 
          if self.completed < 35:
              self.completed += 0.03
              self.progress.setValue(self.completed)
        self.image_out_grad = image_out_grad
        self.image_out_angle = image_out_angle
        self.progress.setValue(self.completed)
        tab_Var = mplt_plot(self.tab,image_out_grad)
        self.t_index = self.tabWidget.addTab(tab_Var, 'Gradient')
        self.tabWidget.setCurrentIndex(self.t_index)
        QMessageBox.about(self,"Status!", "Gradient image Generated!")
        self.nonmaxima() 

    def nonmaxima(self):
        nonmaxima_img = np.array(self.image_out_grad.copy())
        imagea = np.array(self.image_out_angle.copy())
        
        (h,w)=self.image_out_grad.shape
        
        for i in range(h):
            for j in range(w):
                if(i==0 or i==h-1 or j==0 or j==w-1 ):
                    nonmaxima_img[i][j]=0
                    continue
                
                tq=(imagea[i][j])%4
                if(tq==0):
                    if(self.image_out_grad[i,j]<=self.image_out_grad[i,j-1] or self.image_out_grad[i,j]<=self.image_out_grad[i, j+1]):
                        nonmaxima_img[i][j]=0
                if(tq==1):
                    if(self.image_out_grad[i,j]<=self.image_out_grad[i-1,j+1] or self.image_out_grad[i,j]<=self.image_out_grad[i+1,j-1]):
                        nonmaxima_img[i][j]=0
                if(tq==2):
                    if(self.image_out_grad[i,j]<=self.image_out_grad[i-1,j] or self.image_out_grad[i,j]<=self.image_out_grad[i+1,j]):
                        nonmaxima_img[i][j]=0
                if(tq == 3):
                    if(self.image_out_grad[i, j] <= self.image_out_grad[i-1, j-1] or self.image_out_grad[i, j] <= self.image_out_grad[i+1, j+1]):
                        nonmaxima_img[i][j]=0
            if self.completed < 40:
              self.completed += 0.1
              self.progress.setValue(self.completed)
        
        self.nonmaxima_img = nonmaxima_img 
        self.progress.setValue(self.completed)
        tab_Var = mplt_plot(self.tab,nonmaxima_img)
        self.t_index = self.tabWidget.addTab(tab_Var, 'Non-Maximum Supressed')
        self.tabWidget.setCurrentIndex(self.t_index)
        QMessageBox.about(self,"Status!", "Non-max image Generated!")
        #        '''Input Window for Max and Min Threshold'''
        input_dialog = QtWidgets.QDialog()
        input_ui = Threshold.Ui_Dialog()
        input_ui.setupUi(input_dialog)
        input_dialog.show()

        if input_dialog.exec():
            thes_l, Thresh_h = input_ui.onOk()
            if thes_l and Thresh_h:
                thresh = thes_l, Thresh_h
                self.h_thres = np.max(thresh)# Value
                self.l_thres = np.min(thresh)# Value
                self.thres()
                
    def thres(self):
        im = self.nonmaxima_img    
        Imax = np.max(np.max(self.nonmaxima_img))
        Imin = np.min(np.min(self.nonmaxima_img))
        Il = self.l_thres
        Ih = self.h_thres
        l_thres = Il*(Imax-Imin)+Imin
        h_thres = Ih*(Imax-Imin)+Imin        
        print(l_thres,h_thres)    
        si,sj = np.where(im>h_thres)
        wi,wj = np.where((im>=l_thres) & (im<h_thres))
        zi,zj = np.where(im < l_thres)
        im[si,sj] = np.int32(255)
        im[wi,wj]=np.int32(50)
        im[zi,zj]=np.int32(0)
        s = np.zeros(im.shape)
        s[si,sj] = np.int32(255)
        W = np.zeros(im.shape)
        W[wi,wj] = np.int32(50)

        if self.completed < 60:
          self.completed += 0.1
          self.progress.setValue(self.completed)
        self.threshold=W
        self.strong=s     
        self.l_h_t = im
        tab_Var = mplt_plot(self.tab,im)
        self.t_index = self.tabWidget.addTab(tab_Var, 'strong_Weak')
        self.tabWidget.setCurrentIndex(self.t_index)
        self.progress.setValue(70)
        input_dialog2 = QtWidgets.QDialog()
        input_ui2 = Hist_window.Ui_Dialog()
        input_ui2.setupUi(input_dialog2)
        input_dialog2.show()
        if input_dialog2.exec():
            self.windows_size = input_ui2.onOk()
            if int((self.windows_size) % 2)==0:
                self.windows_size=self.windows_size
            else:
                self.windows_size=self.windows_size+1
        self.hysteresis()        

    def hysteresis(self):
        finalEdges = self.strong.copy()
        thresholdedEdges = self.l_h_t
        currentPixels=[]
        wr=int(np.floor(self.windows_size/2))
        wc=int(np.round(self.windows_size/2))

        for r in range(wr, finalEdges.shape[0]-wr):
            for c in range(wc, finalEdges.shape[1]-wc):
                if thresholdedEdges[r, c] != 50:
                    continue #Not a weak pixel
     
    			#Get 3x3 patch	
                localPatch = thresholdedEdges[r-wr:r+wc,c-wr:c+wc]
                patchMax = localPatch.max()
                if patchMax == 50:
                    currentPixels.append((r, c))
                    finalEdges[r, c] = 255
     
    	#Extend strong edges based on current pixels
        while len(currentPixels) > 0:
            newPix = []
            for r, c in currentPixels:
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        if dr == 0 and dc == 0: continue
                        r2 = r+dr
                        c2 = c+dc
                        if thresholdedEdges[r2, c2] == 50 and finalEdges[r2, c2] == 0:
    						#Copy this weak pixel to final result
                            newPix.append((r2, c2))
                            finalEdges[r2, c2] = 255
            currentPixels = newPix
            if self.completed < 95:
                self.completed += 0.05
                self.progress.setValue(self.completed)
        tab_Var = mplt_plot(self.tab,finalEdges)
        self.t_index = self.tabWidget.addTab(tab_Var, 'Edge_Image')
        self.tabWidget.setCurrentIndex(self.t_index)      
        self.progress.setValue(100)
        self.statusBar().showMessage('Done!') 

    def canny_edge(self):
        self.G_Blur()

    def close_application(self):
        choice = QtWidgets.QMessageBox.question(self, 'Warning!',
                                            "Do you really want to Exit?",
                                            QtWidgets.QMessageBox.Yes | 
                                            QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            print("App Closed!")
            sys.exit()
        else:
            pass

    def infile_error(self):
        choice = QtWidgets.QMessageBox.question(self, 'File Error!',
                                        "No File Selected  \nWant to Select File?",
                                        QtWidgets.QMessageBox.Yes | 
                                        QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            self.File_Open_window()

###############################################################################
def run():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
    app.setStyleSheet('QMainWindow{background-color: white;}')
    GUI = Window()              
    GUI.show()
    sys.exit(app.exec_())
###############################################################################   
if __name__ == "__main__":
    run()

    



