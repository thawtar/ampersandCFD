from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QMainWindow
from PySide6 import QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from dialogBoxes import sphereDialogDriver, inputDialogDriver
import vtk
import sys
from time import sleep

# Connection to the Ampersand Backend
from project import ampersandProject
from primitives import ampersandPrimitives, ampersandIO


loader = QUiLoader()

# This function reads STL file and extracts the surface patch names.
def readSTL(stlFileName="cylinder.stl"):
    surfaces = [] # to store the surfaces in the STL file
    try:
        f = open(stlFileName, "r")
        for x in f:
            
            items = x.split(" ")
            if(items[0]=='solid'):
                surfaces.append(items[1][:-1])
                #print(items[1][:-1])
        f.close()
    except:
        print("Error while opening file: ",stlFileName)
    return surfaces


# This is the main window class
class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.surfaces = []
        self.project = ampersandProject(GUIMode=True,window=self)
        # disable all the buttons and input fields
        self.disableButtons()

    def disableButtons(self):
        self.window.pushButtonSTLImport.setEnabled(False)
        self.window.pushButtonSphere.setEnabled(False)
        self.window.pushButtonBox.setEnabled(False)
        self.window.pushButtonCylinder.setEnabled(False)
        self.window.radioButtonInternal.setEnabled(False)
        self.window.radioButtonExternal.setEnabled(False)
        self.window.checkBoxOnGround.setEnabled(False)
        self.window.pushButtonSTLProperties.setEnabled(False)
        self.window.pushButtonPhysicalProperties.setEnabled(False)
        self.window.pushButtonBoundaryCondition.setEnabled(False)
        self.window.pushButtonNumerics.setEnabled(False)
        self.window.pushButtonControls.setEnabled(False)
        #self.window.pushButtonCreate.setEnabled(False)
        #self.window.pushButtonOpen.setEnabled(False)
        self.window.pushButtonGenerate.setEnabled(False)
        self.window.lineEditMinX.setEnabled(False)
        self.window.lineEditMinY.setEnabled(False)
        self.window.lineEditMinZ.setEnabled(False)
        self.window.lineEditMaxX.setEnabled(False)
        self.window.lineEditMaxY.setEnabled(False)
        self.window.lineEditMaxZ.setEnabled(False)
        self.window.lineEdit_nX.setEnabled(False)
        self.window.lineEdit_nY.setEnabled(False)
        self.window.lineEdit_nZ.setEnabled(False)

    def enableButtons(self):
        self.window.pushButtonSTLImport.setEnabled(True)
        self.window.pushButtonSphere.setEnabled(True)
        self.window.pushButtonBox.setEnabled(True)
        self.window.pushButtonCylinder.setEnabled(True)
        self.window.radioButtonInternal.setEnabled(True)
        self.window.radioButtonExternal.setEnabled(True)
        self.window.checkBoxOnGround.setEnabled(True)
        self.window.pushButtonSTLProperties.setEnabled(True)
        self.window.pushButtonPhysicalProperties.setEnabled(True)
        self.window.pushButtonBoundaryCondition.setEnabled(True)
        self.window.pushButtonNumerics.setEnabled(True)
        self.window.pushButtonControls.setEnabled(True)
        self.window.pushButtonCreate.setEnabled(True)
        self.window.pushButtonOpen.setEnabled(True)
        self.window.pushButtonGenerate.setEnabled(True)
        self.window.lineEditMinX.setEnabled(True)
        self.window.lineEditMinY.setEnabled(True)
        self.window.lineEditMinZ.setEnabled(True)
        self.window.lineEditMaxX.setEnabled(True)
        self.window.lineEditMaxY.setEnabled(True)
        self.window.lineEditMaxZ.setEnabled(True)
        self.window.lineEdit_nX.setEnabled(True)
        self.window.lineEdit_nY.setEnabled(True)
        self.window.lineEdit_nZ.setEnabled(True)

    def load_ui(self):
        ui_file = QFile("ampersandInputForm.ui")
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()
        self.setWindowTitle("Ampersand Input Form")
        self.prepare_vtk()
        self.prepare_subWindows()
        self.prepare_events()

    def __del__(self):
        pass

    def openCADDialog(self):
        fname,ftype = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 
        'c:\\',"CAD files (*.brep *.igs *.iges)")
        if(fname==""):
            return -1 # CAD file not loaded
        else:
            print("Current CAD File: ",fname)
            return fname
        
    def openSTLDialog(self):
        fname,ftype = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 
        'c:\\',"STL files (*.stl *.obj)")
        if(fname==""):
            return -1 # STL file not loaded
        else:
            #print("Current STL File: ",fname)
            return fname

    def openSTL(self):
        stlFileName = self.openSTLDialog()
        if(stlFileName==-1):
            pass
        else:
            #print("Copying stl file")
            stl = stlFileName #self.copySTL(stlFileName=stlFileName)
            if(stl!=-1):
                self.showSTL(stlFile=stl)
                
    # manage sub windows
    def prepare_subWindows(self):
        self.createCaseWindow = None

    def prepare_vtk(self):
        # Prepare the VTK widget to show the STL
        self.vl = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.window.widget)
        self.vl.addWidget(self.vtkWidget)
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.vtkWidget.resize(891,471)
        # change the background color to black
        self.ren.SetBackground(0, 0, 0)
        #self.ren.SetBackground(0.1, 0.2, 0.4)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

    # this function will read STL file and show it in the VTK renderer
    def showSTL(self,stlFile=r"C:\Users\mrtha\Desktop\GitHub\foamAutoGUI\src\pipe.stl"):
        # Read stl
        try:
            self.reader = vtk.vtkSTLReader()
            self.reader.SetFileName(stlFile)
            self.render3D()
        except:
            print("Reading STL not successful. Try again")

    def render3D(self):  # self.ren and self.iren must be used. other variables are local variables
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.reader.GetOutputPort())
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().EdgeVisibilityOn()
        colors = vtk.vtkNamedColors()
        self.ren.SetBackground(colors.GetColor3d("SlateGray"))
        self.ren.AddActor(actor)
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.iren.SetInteractorStyle(style)
        camera = vtk.vtkCamera()
        camera.SetPosition(0, 1, 0)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 0, 1)
        camera.Azimuth(30)
        camera.Elevation(30)
        self.ren.SetActiveCamera(camera)
        self.ren.ResetCamera()
        self.ren.ResetCameraClippingRange()
        # add coordinate axes
        axes = vtk.vtkAxesActor()
        self.ren.AddActor(axes)
        # move the axes to the lower left corner
        # I am not sure what Copilot does here
        self.ren.GetActiveCamera().Azimuth(30)
        self.ren.GetActiveCamera().Elevation(30)
        self.ren.GetActiveCamera().Roll(-20)
        self.ren.ResetCamera()
        self.ren.ResetCameraClippingRange()
        # set the background color
        self.ren.SetBackground(0.1, 0.2, 0.4)
        


        #renWin.Render()
        self.iren.Start()

    
    def loadSTL(self,stlFile = r"C:\Users\mrtha\Desktop\GitHub\foamAutoGUI\src\pipe.stl"):
        ampersandIO.printMessage("Loading STL file")
        stl_name = stlFile.split("/")[-1]
        if(stl_name in self.surfaces):
            self.updateStatusBar("STL file already loaded")
            return
        self.surfaces.append(stl_name)
        print(self.surfaces)
        idx = len(self.surfaces)
        self.window.listWidgetObjList.insertItem(idx,stl_name)
        message = "Loaded STL file: "+stlFile
        self.updateStatusBar(message) 

    def update_list(self):
        self.window.listWidgetObjList.clear()
        for i in range(len(self.project.stl_files)):
            self.window.listWidgetObjList.insertItem(i,self.project.stl_files[i]['name'])


    def updatePropertyBox(self):
        # find the selected item in the list
        item = self.window.listWidgetObjList.currentItem()


    def updateStatusBar(self,message="Go!"):
        self.window.statusbar.showMessage(message)
        self.window.plainTextTerminal.appendPlainText(message)

    def readyStatusBar(self):
        # pause 1 millisecond
        sleep(0.001)
        self.window.statusbar.showMessage("Ready")

    def prepare_events(self):
        # Initiate the button click maps
        self.window.pushButtonSTLImport.clicked.connect(self.importSTL)
        self.window.pushButtonSphere.clicked.connect(self.createSphere)
        self.window.actionNew_Case.triggered.connect(self.createCase)
        self.window.actionOpen_Case.triggered.connect(self.openCase)
        self.window.pushButtonCreate.clicked.connect(self.createCase)
        self.window.pushButtonOpen.clicked.connect(self.openCase)
        self.window.actionExit.triggered.connect(self.close)
        self.window.pushButtonGenerate.clicked.connect(self.generateCase)
        self.window.statusbar.showMessage("Ready")

#----------------- Event Handlers -----------------#
    def importSTL(self):
        #self.updateStatusBar("Opening STL")
        #self.openSTL()
        #self.readyStatusBar()
        self.project.add_stl_file()
        self.showSTL(stlFile=self.project.current_stl_file)
        self.update_list()
        #self.project.list_stl_files()
    
    def createSphere(self):
        #print("Create Sphere")
        ampersandIO.printMessage("Creating Sphere",GUIMode=True,window=self)
        # create a sphere dialog
        sphereData = sphereDialogDriver()
        if sphereData == None:
            ampersandIO.printError("Sphere Dialog Box Closed",GUIMode=True)
        else:
            x,y,z,r = sphereData
            print("Center: ",x,y,z)
            print("Radius: ",r)
        self.readyStatusBar()

    
    def chooseInternalFlow(self):
        print("Choose Internal Flow")
        self.updateStatusBar("Choosing Internal Flow")

    def createCase(self):

        self.updateStatusBar("Creating Case")
        self.project.set_project_directory(ampersandPrimitives.ask_for_directory(qt=True))
        project_name = ampersandIO.get_input("Enter the project name: ",GUIMode=True)
        if project_name == None:
            ampersandIO.printError("Project Name not entered",GUIMode=True)
            return
        self.project.set_project_name(project_name)
        
        self.project.create_project_path()
        ampersandIO.printMessage("Creating the project",GUIMode=True,window=self)
        ampersandIO.printMessage(f"Project path: {self.project.project_path}",GUIMode=True,window=self)
        self.project.create_project()
        self.project.create_settings()
        ampersandIO.printMessage("Preparing for mesh generation",GUIMode=True,window=self)
        self.project.set_global_refinement_level()
        # Now enable the buttons
        self.enableButtons()
        self.readyStatusBar()

    def openCase(self):
        self.updateStatusBar("Opening Case")
        projectFound = self.project.set_project_path(ampersandPrimitives.ask_for_directory(qt=True))
        ampersandIO.printMessage(f"Project path: {self.project.project_path}",GUIMode=True,window=self)
        if projectFound==-1:
            ampersandIO.printError("No project found. Exiting the program",GUIMode=True)
            return -1
        ampersandIO.printMessage("Loading the project",GUIMode=True,window=self)
        self.project.go_inside_directory()
        
        self.project.load_settings()
        self.project.check_0_directory()
        ampersandIO.printMessage("Project loaded successfully",GUIMode=True,window=self)
        self.project.summarize_project()

    def generateCase(self):
        self.updateStatusBar("Analyzing Case")
        if(len(self.project.stl_files)>0):
            self.project.analyze_stl_file()
        self.updateStatusBar("Creating Project Files")
        self.project.useFOs = True
        self.project.set_post_process_settings()
        #project.list_stl_files()
        self.project.summarize_project()
        #project.analyze_stl_file()
    
        self.project.write_settings()
        self.project.create_project_files()

        
#-------------- End of Event Handlers -------------#


def main():

    app = QApplication(sys.argv)
    w = mainWindow()
    w.window.show()
    app.exec()

if __name__ == "__main__":
    main()
