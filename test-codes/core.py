
from trame.app import get_server
from trame.decorators import TrameApp, change, controller
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vuetify, vtk

# vtk module to handle all 3D objects
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkPolyDataMapper,
)

from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkFiltersCore import vtkContourFilter
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader
from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor
from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor

# Required for interactor initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa

# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
import vtkmodules.vtkRenderingOpenGL2  # noqa
import os
from trame.widgets import vuetify
#import vuetify
from tkinter import filedialog


# ---------------------------------------------------------
# Engine class
# ---------------------------------------------------------

@TrameApp()
class ampersand:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue2")
        self.stl_file = "cad.stl"
        if self.server.hot_reload:
            self.server.controller.on_server_reload.add(self._build_ui)
        self._prepare_vtk()
        self.ui = self._build_ui()

        # Set state variable
        self.state.trame__title = "AmpersandCFD"
        self.state.resolution = 6
        
    def click_open(self):
        print(f"Open button clicked")
        file_name=self.file_dialog()
        if(file_name != ""):
            self.stl_file = file_name 
            self._prepare_vtk()
            self._update_vtk()
            self._build_ui()
        else:
            print("No file selected")
        #print(f"Opening {file_name}")
        #self.stl_file = file_name

    def file_dialog(self):
        # open file dialog from tkinter
        file_name = filedialog.askopenfilename()
        return file_name

    def add_box(self):
        print(f"Add box clicked")
        # Show a pop-up dialog to ask for dimensions
        with vuetify.VDialog(v_model="dialog", max_width="500px"):
            with vuetify.VCard():
                with vuetify.VCardTitle("Add Box"):
                    pass
                

    def add_sphere(self):
        print(f"Add sphere clicked")

    def show_wireframe(self):
        print(f"Show wireframe clicked")

    def show_surface(self):
        print(f"Show surface clicked")
    
    def show_surface_with_edges(self):
        print(f"Show surface with edges clicked")
        

    
    
    @property
    def state(self):
        return self.server.state

    @property
    def ctrl(self):
        return self.server.controller

    def _prepare_vtk(self,*args,**kwargs):
        self.renderer = vtkRenderer()
        self.renderWindow = vtkRenderWindow()
        self.renderWindow.AddRenderer(self.renderer)

        renderWindowInteractor = vtkRenderWindowInteractor()
        renderWindowInteractor.SetRenderWindow(self.renderWindow)
        renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        reader = vtkSTLReader()
        reader.SetFileName(self.stl_file)
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtkActor()
        actor.SetMapper(mapper)
        
        self.renderer.AddActor(actor)
        self.renderer.ResetCamera()

    def _build_ui(self, *args, **kwargs):
        self.state.menu_items = ["one", "two", "three"]
        with SinglePageWithDrawerLayout(self.server) as layout:
            # Toolbar
            layout.title.set_text("AmpersandCFD")
            layout.icon.set_text("<img src='/Users/thawtar/Desktop/CFD_Monkey/ampersandCFD/src/ampersandCFD/components/logo.svg' alt='icon' width='24' height='24'>")
            layout.footer.set_text("Developed by CFD Monkey")
            with layout.toolbar:
                vuetify.VSpacer()
                # add 3 buttons here
                with vuetify.VBtn(click=self.show_surface, large=False, rounded=False,dense=True):
                    vuetify.VIcon("mdi-rectangle")
                with vuetify.VBtn(click=self.show_surface_with_edges, large=False, rounded=False,dense=True):
                    vuetify.VIcon("mdi-rectangle-outline")
                with vuetify.VBtn(click=self.show_wireframe, large=False, rounded=False,dense=True, v_tooltip="Show Wireframe"):
                    vuetify.VIcon("mdi-vector-rectangle")


                
            with layout.drawer:
                vuetify.VSpacer()
                with vuetify.VCard():
                    vuetify.VCardTitle("Geometry")
                    vuetify.VSpacer()
                    with vuetify.VBtn(click=self.click_open, large=False, rounded=False,dense=True):
                        vuetify.VIcon("mdi-open-in-app")
                        vuetify.VCardTitle("Open")
                    with vuetify.VBtn(click=self.add_box, large=False, rounded=False,dense=True):
                        vuetify.VIcon("mdi-rectangle-outline")
                    with vuetify.VBtn(click=self.add_sphere, large=False, rounded=False,dense=True):
                        vuetify.VIcon("mdi-circle-outline")
                    labels = ["minx", "miny", "minz", "maxx", "maxy", "maxz","nx","ny","nz"]
                with vuetify.VCard():
                    with vuetify.VCardTitle("Domain"):
                        vuetify.VSpacer()
                        with vuetify.VRow():
                            for i in range(9): 
                                with vuetify.VCol(cols=4):
                                    with vuetify.VTextField(label=labels[i], v_model=(f"textbox_{labels[i]}",0), dense=True):
                                        pass
                # Settings for snappyHexMesh 
                with vuetify.VCard():
                    with vuetify.VCardTitle("snappyHexMesh"):
                        vuetify.VSpacer()
                        with vuetify.VSwitch(label="Toggle Button 1"):
                            pass
                        with vuetify.VSwitch(label="Toggle Button 2"):
                            pass
                        with vuetify.VSwitch(label="Toggle Button 3"):
                            pass
           
            # Main content
            with layout.content:
                with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
                    view = vtk.VtkLocalView(self.renderWindow)

            # Footer
            # layout.footer.hide()

            return layout
    
    def _update_vtk(self,*args, **kwargs):
        # Main content
        with SinglePageWithDrawerLayout(self.server) as layout:
            # Toolbar
            with layout.content:
                with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
                    view = vtk.VtkLocalView(self.renderWindow)

            # Footer
            # layout.footer.hide()

            return layout
