from pathlib import Path
from typing import Optional, Union
from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QMainWindow
from PySide6 import QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from ampersandCFD.services.mod_service import ModService
from ampersandCFD.gui.dialogBoxes import sphereDialogDriver, yesNoCancelDialogDriver
# ----------------- VTK Libraries ----------------- #
import vtk
# noinspection PyUnresolvedReferences
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
# ------------------------------------------------- #
import sys
from time import sleep

# Connection to the Ampersand Backend
from ampersandCFD.models.project import AmpersandProject
from ampersandCFD.utils.io import AmpersandDataInput, IOUtils
from ampersandCFD.services.project_service import ProjectService


loader = QUiLoader()

# This function reads STL file and extracts the surface patch names.


def readSTL(stlFileName="cylinder.stl"):
    surfaces = []  # to store the surfaces in the STL file
    try:
        f = open(stlFileName, "r")
        for x in f:

            items = x.split(" ")
            if (items[0] == 'solid'):
                surfaces.append(items[1][:-1])
                # IOUtils.print(items[1][:-1])
        f.close()
    except:
        IOUtils.print("Error while opening file: ", stlFileName)
    return surfaces


# This is the main window class
class MainWindow(QMainWindow):
    project: AmpersandProject
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.current_stl_path: Optional[Path] = None
        self.surfaces = []
        self.project_opened = False
        self.minx, self.miny, self.minz = 0.0, 0.0, 0.0
        self.maxx, self.maxy, self.maxz = 0.0, 0.0, 0.0
        self.nx, self.ny, self.nz = 0, 0, 0
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
        self.window.pushButtonDomainAuto.setEnabled(False)
        self.window.pushButtonDomainManual.setEnabled(False)
        # self.window.pushButtonCreate.setEnabled(False)
        # self.window.pushButtonOpen.setEnabled(False)
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
        # change color of widget
        self.window.widget.setStyleSheet('''background-color: lightgrey;''')
        # change color of text box

        # self.window.plainTextTerminal.setStyleSheet('''
        #    QPlainTextEdit {
        #        background-color: lightgrey;
        #        color: green;
        #                                            }''')
        self.window.plainTextTerminal.appendPlainText(
            "Welcome to Ampersand CFD GUI")

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
        self.window.pushButtonDomainAuto.setEnabled(True)
        self.window.pushButtonDomainManual.setEnabled(True)
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
        ui_file = QFile("qfiles/ampersandInputForm.ui")
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()
        self.setWindowTitle("Ampersand Input Form")
        self.prepare_vtk()
        self.prepare_subWindows()
        self.prepare_events()

        IOUtils.window = self
        IOUtils.GUIMode = True

    def __del__(self):
        pass

    def openCADDialog(self):
        fname, ftype = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',
                                                             'c:\\', "CAD files (*.brep *.igs *.iges)")
        if (fname == ""):
            return -1  # CAD file not loaded
        else:
            IOUtils.print("Current CAD File: ", fname)
            return fname

    def openSTLDialog(self):
        fname, ftype = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',
                                                             'c:\\', "STL files (*.stl *.obj)")
        if (fname == ""):
            return -1  # STL file not loaded
        else:
            # IOUtils.print("Current STL File: ",fname)
            return fname

    def openSTL(self):
        stlFileName = self.openSTLDialog()
        if (stlFileName == -1):
            pass
        else:
            # IOUtils.print("Copying stl file")
            stl = stlFileName  # self.copySTL(stlFileName=stlFileName)
            if (stl != -1):
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
        self.vtkWidget.resize(891, 471)
        # change the background color to black
        colors = vtk.vtkNamedColors()
        whiteColor = colors.GetColor3d("White")
        blackColor = colors.GetColor3d("Black")
        self.ren.GradientBackgroundOn()
        self.ren.SetBackground(whiteColor)
        self.ren.SetBackground2(blackColor)
        # self.ren.SetBackground(0, 0, 0)
        # self.ren.SetBackground(0.1, 0.2, 0.4)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        # self.reader = vtk.vtkSTLReader()
        # self.render3D()
        self.initializeVTK()
        # self.iren.Initialize()
        # self.iren.Start()

    # this function will read STL file and show it in the VTK renderer
    def showSTL(self, stlFile: Union[str, Path]):
        # Read stl
        try:
            self.reader = vtk.vtkSTLReader()
            self.reader.SetFileName(str(stlFile))
            self.render3D()
        except:
            IOUtils.print("Reading STL not successful. Try again")

    def initializeVTK(self):
        # Create a mapper
        # mapper = vtk.vtkPolyDataMapper()
        # mapper.SetInputConnection(self.reader.GetOutputPort())
        # Create an actor
        actor = vtk.vtkActor()
        # actor.SetMapper(mapper)
        actor.GetProperty().EdgeVisibilityOn()
        colors = vtk.vtkNamedColors()
        whiteColor = colors.GetColor3d("White")
        blackColor = colors.GetColor3d("Black")
        # deepBlue = colors.GetColor3d("DeepBlue")
        # self.ren.SetBackground(colors.GetColor3d("SlateGray"))
        # set background color as gradient
        self.ren.GradientBackgroundOn()
        self.ren.SetBackground(whiteColor)
        self.ren.SetBackground2(blackColor)
        self.ren.AddActor(actor)
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.iren.SetInteractorStyle(style)
        camera = vtk.vtkCamera()
        camera.SetPosition(-1, 1, 1)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 0, 1)
        self.ren.SetActiveCamera(camera)
        self.iren.Initialize()
        # add coordinate axes
        axes = vtk.vtkAxesActor()
        widget = vtkOrientationMarkerWidget()
        # renderWindowInteractor = vtkRenderWindowInteractor()
        rgba = [0] * 4
        colors.GetColor('Carrot', rgba)
        widget.SetOutlineColor(rgba[0], rgba[1], rgba[2])
        widget.SetOrientationMarker(axes)
        widget.SetInteractor(self.iren)
        widget.SetViewport(0.0, 0.0, 0.4, 0.4)
        widget.SetEnabled(1)
        widget.InteractiveOn()
        self.ren.AddActor(axes)
        self.iren.Start()

    def render3D(self):  # self.ren and self.iren must be used. other variables are local variables
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.reader.GetOutputPort())
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().EdgeVisibilityOn()
        # set random colors to the actor

        actor.GetProperty().SetColor(0.5, 0.5, 0.5)
        self.ren.AddActor(actor)

        # self.iren.Start()

    def add_object_to_VTK(self, object, objectName="sphere", opacity=0.5, removePrevious=False):
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(object.GetOutputPort())
        # Create an actor
        actor = vtk.vtkActor()
        actor.GetProperty().SetOpacity(opacity)
        actor.GetProperty().SetColor(0.5, 0.5, 0.5)
        actor.GetProperty().SetObjectName(objectName)
        actor.GetProperty().EdgeVisibilityOn()
        actor.SetMapper(mapper)
        # remove the previous object
        if (removePrevious):
            currentActors = self.ren.GetActors()
            for act in currentActors:
                if (act.GetProperty().GetObjectName() == objectName):
                    self.ren.RemoveActor(act)
        self.ren.AddActor(actor)
        self.iren.Start()

    def add_sphere_to_VTK(self):
        # Create a sphere
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(0.0, 0.0, 0.0)
        sphere.SetRadius(1.0)
        self.add_object_to_VTK(
            sphere, objectName="sphere", removePrevious=True)

    def add_box_to_VTK(self, minX=0.0, minY=0.0, minZ=0.0, maxX=1.0, maxY=1.0, maxZ=1.0, boxName="box"):
        # Create a cube
        cube = vtk.vtkCubeSource()
        cube.SetXLength(maxX-minX)
        cube.SetYLength(maxY-minY)
        cube.SetZLength(maxZ-minZ)
        cube.SetCenter((maxX+minX)/2, (maxY+minY)/2, (maxZ+minZ)/2)
        # make box transparent

        cubeMapper = vtk.vtkPolyDataMapper()
        cubeMapper.SetInputConnection(cube.GetOutputPort())
        cubeActor = vtk.vtkActor()
        cubeActor.GetProperty().SetOpacity(0.5)
        cubeActor.GetProperty().SetColor(0.5, 0.5, 0.5)
        cubeActor.GetProperty().SetObjectName(boxName)
        cubeActor.SetMapper(cubeMapper)
        # remove the previous box
        currentActors = self.ren.GetActors()
        for actor in currentActors:
            if (actor.GetProperty().GetObjectName() == boxName):
                self.ren.RemoveActor(actor)
        self.ren.AddActor(cubeActor)
        currentActors = self.ren.GetActors()

        # self.ren.ResetCamera()
        self.iren.Start()

    def loadSTL(self, stlFile=r"C:\Users\mrtha\Desktop\GitHub\foamAutoGUI\src\pipe.stl"):
        IOUtils.print("Loading STL file")
        stl_name = stlFile.split("/")[-1]
        if (stl_name in self.surfaces):
            self.updateStatusBar("STL file already loaded")
            return
        self.surfaces.append(stl_name)
        IOUtils.print(self.surfaces)
        idx = len(self.surfaces)
        self.window.listWidgetObjList.insertItem(idx, stl_name)
        message = "Loaded STL file: "+stlFile
        self.updateStatusBar(message)

    def update_list(self):
        self.window.listWidgetObjList.clear()
        for i, stl_path in enumerate(self.project.get_stl_paths()):
            self.window.listWidgetObjList.insertItem(i, stl_path.stem)

    def updatePropertyBox(self):
        # find the selected item in the list
        item = self.window.listWidgetObjList.currentItem()
        IOUtils.print("Selected Item: ", item.text())

    def updateStatusBar(self, message="Go!"):
        self.window.statusbar.showMessage(message)
        self.window.plainTextTerminal.appendPlainText(message)

    def updateTerminal(self, message="Go!"):
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
        self.window.radioButtonInternal.clicked.connect(
            self.chooseInternalFlow)
        self.window.radioButtonExternal.clicked.connect(
            self.chooseExternalFlow)
        self.window.listWidgetObjList.itemClicked.connect(
            self.updatePropertyBox)
        self.window.pushButtonDomainAuto.clicked.connect(self.autoDomain)
        self.window.pushButtonDomainManual.clicked.connect(self.manualDomain)
        # self.window.checkBoxOnGround.clicked.connect(self.chooseExternalFlow)
        self.window.statusbar.showMessage("Ready")

# ----------------- Event Handlers -----------------#
    def importSTL(self):
        # self.updateStatusBar("Opening STL")
        # self.openSTL()
        # self.readyStatusBar()
        current_stl_file = ModService.add_geometry(self.project)
        assert current_stl_file is not None, "STL File not selected"
        self.showSTL(stlFile=current_stl_file)
        self.update_list()
        # self.project.list_stl_files()

    def createSphere(self):
        # IOUtils.print("Create Sphere")
        IOUtils.print("Creating Sphere")
        # create a sphere dialog
        sphereData = sphereDialogDriver()
        if sphereData == None:
            IOUtils.error("Sphere Dialog Box Closed")
        else:
            x, y, z, r = sphereData
            IOUtils.print("Center: ", x, y, z)
            IOUtils.print("Radius: ", r)
        self.readyStatusBar()

    def chooseInternalFlow(self):
        # IOUtils.print("Choose Internal Flow")
        self.project.settings.mesh.internalFlow = True
        self.window.checkBoxOnGround.setEnabled(False)
        self.updateStatusBar("Choosing Internal Flow")
        sleep(0.001)
        self.readyStatusBar()

    def chooseExternalFlow(self):
        self.project.settings.mesh.internalFlow = False
        self.window.checkBoxOnGround.setEnabled(True)
        self.project.settings.mesh.onGround = self.window.checkBoxOnGround.isChecked(
        )
        self.project.settings.mesh.onGround = self.window.checkBoxOnGround.isChecked()
        self.updateStatusBar("Choosing External Flow")
        sleep(0.001)
        self.readyStatusBar()

    def createCase(self):
        if self.project_opened:
            # ask yes or no or cancel
            yNC = yesNoCancelDialogDriver(
                "Save changes to current case files before creating a New Case", "Save Changes")
            if yNC == 1:  # if yes
                # save the project
                
                self.current_stl_path = ModService.add_geometry(self.project)
                ProjectService.write_settings(self.project)

                self.disableButtons()
                self.ren.RemoveAllViewProps()
            elif yNC == -1:  # if no
                # close the project
                self.project = None
                self.project_opened = False
                self.disableButtons()
                self.ren.RemoveAllViewProps()
            else:  # if cancel
                return

        self.updateStatusBar("Creating New Case")

        # clear vtk renderer
        self.ren.RemoveAllViewProps()
        # clear the list widget
        self.window.listWidgetObjList.clear()
        IOUtils.window = self.window
        IOUtils.GUIMode = True

        parent_directory = IOUtils.ask_for_directory(qt=True)
        project_name = IOUtils.get_input("Enter the project name: ")
        project_path = f"{parent_directory}/{project_name}"

        self.project = ProjectService.create_project(project_path)

        self.project.settings.mesh.refAmount = AmpersandDataInput.get_mesh_refinement_amount()
        # Now enable the buttons
        self.enableButtons()
        self.readyStatusBar()
        self.project_opened = True
        IOUtils.print(
            f"Project {project_name} created")

        # change window title
        self.window.setWindowTitle(f"Case Creator: {project_name}")
        self.readyStatusBar()

    def openCase(self):
        if self.project_opened:
            # ask yes or no or cancel
            yNC = yesNoCancelDialogDriver(
                "Save changes to current case files before creating a New Case", "Save Changes")
            if yNC == 1:  # if yes
                # save the project

                self.current_stl_path =  ModService.add_geometry(self.project)
                ProjectService.write_settings(self.project)
                self.disableButtons()
                self.ren.RemoveAllViewProps()
            elif yNC == -1:  # if no
                # close the project
                self.project = None # type: ignore
                self.project_opened = False
                self.disableButtons()
                self.ren.RemoveAllViewProps()
            else:  # if cancel
                self.readyStatusBar()
                return
        self.updateStatusBar("Opening Case")

        # clear vtk renderer
        self.ren.RemoveAllViewProps()
        # clear the list widget
        self.window.listWidgetObjList.clear()
        
        project_path = IOUtils.ask_for_directory(qt=True)
        assert project_path is not None, "Project Path not selected"
        IOUtils.print(f"Project path: {project_path}")
        IOUtils.print("Loading the project")

        self.project = ProjectService.load_project(project_path)

        self.project.summarize_project()
        self.enableButtons()
        self.autoDomain()
        self.update_list()
        stl_file_paths = self.project.get_stl_paths()
        for stl_file in stl_file_paths:
            self.showSTL(stlFile=stl_file)
        self.readyStatusBar()
        self.project_opened = True
        IOUtils.print(
            f"Project {self.project.name} created")

        # change window title
        self.setWindowTitle(f"Case Creator: {self.project.name}")
        self.readyStatusBar()

    def generateCase(self):
        self.updateStatusBar("Analyzing Case")
        self.updateStatusBar("Creating Project Files")
        self.project.settings.set_post_process_settings(True)
        self.project.summarize_project()
        ProjectService.write_project(self.project)
        self.readyStatusBar()

    def autoDomain(self):
        onGround = self.window.checkBoxOnGround.isChecked()
        self.project.settings.mesh.onGround = onGround
        IOUtils.print("On Ground: ", onGround)
        minx = self.project.settings.mesh.domain.minx
        miny = self.project.settings.mesh.domain.miny
        minz = self.project.settings.mesh.domain.minz
        maxx = self.project.settings.mesh.domain.maxx
        maxy = self.project.settings.mesh.domain.maxy
        maxz = self.project.settings.mesh.domain.maxz
        nx = self.project.settings.mesh.domain.nx
        ny = self.project.settings.mesh.domain.ny
        nz = self.project.settings.mesh.domain.nz
        self.window.lineEditMinX.setText(f"{minx:.2f}")
        self.window.lineEditMinY.setText(f"{miny:.2f}")
        self.window.lineEditMinZ.setText(f"{minz:.2f}")
        self.window.lineEditMaxX.setText(f"{maxx:.2f}")
        self.window.lineEditMaxY.setText(f"{maxy:.2f}")
        self.window.lineEditMaxZ.setText(f"{maxz:.2f}")
        self.window.lineEdit_nX.setText(str(nx))
        self.window.lineEdit_nY.setText(str(ny))
        self.window.lineEdit_nZ.setText(str(nz))
        self.add_box_to_VTK(minX=minx, minY=miny, minZ=minz,
                            maxX=maxx, maxY=maxy, maxZ=maxz, boxName="Domain")

    def manualDomain(self):
        minx = float(self.window.lineEditMinX.text())
        miny = float(self.window.lineEditMinY.text())
        minz = float(self.window.lineEditMinZ.text())
        maxx = float(self.window.lineEditMaxX.text())
        maxy = float(self.window.lineEditMaxY.text())
        maxz = float(self.window.lineEditMaxZ.text())
        nx = int(self.window.lineEdit_nX.text())
        ny = int(self.window.lineEdit_nY.text())
        nz = int(self.window.lineEdit_nZ.text())
        if (nx <= 0 or ny <= 0 or nz <= 0):
            IOUtils.error("Invalid Domain Size")
            self.readyStatusBar()
            return
        if (minx > maxx or miny > maxy or minz > maxz):
            IOUtils.error("Invalid Domain Size")
            self.readyStatusBar()
            return
        self.project.settings.mesh.domain.minx = minx
        self.project.settings.mesh.domain.miny = miny
        self.project.settings.mesh.domain.minz = minz
        self.project.settings.mesh.domain.maxx = maxx
        self.project.settings.mesh.domain.maxy = maxy
        self.project.settings.mesh.domain.maxz = maxz
        self.project.settings.mesh.domain.nx = nx
        self.project.settings.mesh.domain.ny = ny
        self.project.settings.mesh.domain.nz = nz
        self.updateStatusBar("Manual Domain Set")
        self.add_box_to_VTK(minX=minx, minY=miny, minZ=minz,
                            maxX=maxx, maxY=maxy, maxZ=maxz, boxName="Domain")
        self.readyStatusBar()
        # IOUtils.print("Domain: ",minx,miny,minz,maxx,maxy,maxz,nx,ny,nz)


# -------------- End of Event Handlers -------------#


def main():

    app = QApplication(sys.argv)
    w = MainWindow()
    w.window.show()
    app.exec()


if __name__ == "__main__":
    main()
