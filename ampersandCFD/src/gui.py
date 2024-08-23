# Description: This file contains the main class for the Ampersand CFD application. The class is decorated with the TrameApp decorator, which is used to create a Trame application. The class contains methods to handle the opening of a file, adding a box, adding a sphere, showing a wireframe, showing a surface, and showing a surface with edges. The class also contains a method to build the user interface of the application. The user interface contains a toolbar with three buttons, a drawer with buttons to open a file, add a box, and add a sphere, and a main content area with a VtkLocalView widget to display the 3D object. The class also contains a method to update the VtkLocalView widget with the new 3D object.
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
# Definitions for GUI elements
# ---------------------------------------------------------

class gui:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue2")
        self.ui = self._build_ui()

        # Set state variable
        self.state.trame__title = "AmpersandCFD"
        self.state.resolution = 6

    def _build_ui(self):
        return SinglePageWithDrawerLayout(
            toolbar=[vuetify.VSpacer(), vuetify.VBtn(color="primary", dark=True, children=["Open"], on_click=self.click_open)],
            drawer=[
                vuetify.VBtn(color="primary", dark=True, children=["Add Box"], on_click=self.click_add_box),
                vuetify.VBtn(color="primary", dark=True, children=["Add Sphere"], on_click=self.click_add_sphere),
            ],
            content=vuetify.VContainer(children=[vtk.VtkLocalView(renderer=self.renderer)]),
        )
    