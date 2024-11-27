from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QDialog
from PySide6.QtGui import QDoubleValidator
from PySide6 import QtWidgets

import sys
from time import sleep

loader = QUiLoader()

class sphereDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.surfaces = []
        self.centerX = 0.0
        self.centerY = 0.0
        self.centerZ = 0.0
        self.radius = 0.0
        self.created = False
    
    def load_ui(self):
        ui_path = r"C:\Users\Ridwa\Desktop\CFD\01_CFD_Software_Development\ampersandCFD\src\createSphereDialog.ui"
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()
        #self.window.setWindowTitle("Sphere Dialog")
        self.prepare_events()
        # make text box for number only with floating points OK
        self.window.lineEditSphereX.setValidator(QDoubleValidator())
        self.window.lineEditSphereRadius.setValidator(QDoubleValidator(0.0,1e10,3))
        
    
    def prepare_events(self):
        self.window.pushButtonOK.clicked.connect(self.on_pushButtonOK_clicked)
        self.window.pushButtonCancel.clicked.connect(self.on_pushButtonCancel_clicked)
    
    def on_pushButtonOK_clicked(self):
        #print("Push Button OK Clicked")
        self.centerX = float(self.window.lineEditSphereX.text())
        self.centerY = float(self.window.lineEditSphereY.text())
        self.centerZ = float(self.window.lineEditSphereZ.text())
        self.radius = float(self.window.lineEditSphereRadius.text())
        self.created = True
        #print("Center: ",self.centerX,self.centerY,self.centerZ)
        #print("Radius: ",self.radius)
        self.window.close()

    def on_pushButtonCancel_clicked(self):
        print("Push Button Cancel Clicked")
        self.window.close()
        
    def __del__(self):
        pass

class inputDialog(QDialog):
    def __init__(self, prompt="Enter Input"):
        super().__init__()
        
        self.input = None
        self.created = False
        self.prompt = prompt
        self.load_ui()

    def load_ui(self):
        ui_path = r"C:\Users\Ridwa\Desktop\CFD\01_CFD_Software_Development\ampersandCFD\src\inputDialog.ui"
        ui_file = QFile(ui_path)
        #ui_file = QFile("inputDialog.ui")
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()
        self.window.setWindowTitle("Input Dialog")
        self.window.labelPrompt.setText(self.prompt)
        self.prepare_events()
        

    def prepare_events(self):
        self.window.pushButtonOK.clicked.connect(self.on_pushButtonOK_clicked)
        self.window.pushButtonCancel.clicked.connect(self.on_pushButtonCancel_clicked)
    
    def on_pushButtonOK_clicked(self):
        #print("Push Button OK Clicked")
        self.input = self.window.input.text()
        self.window.close()

    def on_pushButtonCancel_clicked(self):
        #print("Push Button Cancel Clicked")
        self.window.close()

#---------------------------------------------------------
# Driver function for different dialog boxes
#---------------------------------------------------------

def sphereDialogDriver():
    dialog = sphereDialog()
    dialog.window.exec()
    dialog.window.show()
    x,y,z = dialog.centerX,dialog.centerY,dialog.centerZ
    r = dialog.radius
    if(dialog.created==False):
        #print("Sphere Dialog Box Closed")
        return None
    return (x,y,z,r)

def inputDialogDriver(prompt="Enter Input"):
    dialog = inputDialog(prompt=prompt)
    dialog.window.exec()
    dialog.window.show()
    input = dialog.input
    if(input==None):
       
        return None
    return input
    

def main():
    pass

if __name__ == "__main__":
    main()