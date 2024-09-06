import trame, trame_vtk
from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout,SinglePageLayout
from trame.ui.vuetify import VAppLayout
from trame.widgets import vuetify, html

from trame.widgets import vuetify, vtk
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkPolyDataMapper,
)

from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

# Required for interactor initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa

# collection of events
from events import events

def main():
    renderer = vtkRenderer()
    renderWindow = vtkRenderWindow()
    renderWindow.AddRenderer(renderer)

    renderWindowInteractor = vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

    cone_source = vtkConeSource()
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(cone_source.GetOutputPort())
    actor = vtkActor()
    actor.SetMapper(mapper)

    renderer.AddActor(actor)
    renderer.ResetCamera()
    
    # Create the Trame application
    server = get_server(client_type="vue2")
    evs = events()
    state, ctrl = server.state, server.controller

    with VAppLayout(server) as layout:
        # Left drawer (unchanged)
        with vuetify.VNavigationDrawer(app=True, left=True, v_model=("leftDrawer", True)):
            html.Div("Left Drawer Content")

        # Right drawer (toolbox) with VCards
        with vuetify.VNavigationDrawer(app=True, right=True, v_model=("rightDrawer", True), width=300):
            with vuetify.VContainer(fluid=True):
                vuetify.VSubheader("Toolbox")
                
                # Card 1
                with vuetify.VCard(class_="mb-4"):
                    vuetify.VCardTitle("Card 1")
                    with vuetify.VCardText():
                        vuetify.VBtn(color="primary", block=True, class_="mb-2", children="Button 1")
                        vuetify.VBtn(color="secondary", block=True, children="Button 2")

                # Card 2
                with vuetify.VCard(class_="mb-4"):
                    vuetify.VCardTitle("Card 2")
                    with vuetify.VCardText():
                        vuetify.VBtn(color="success", block=True, class_="mb-2", children="Button 3")
                        vuetify.VBtn(color="info", block=True, children="Button 4")

                # Card 3
                with vuetify.VCard():
                    vuetify.VCardTitle("Card 3")
                    with vuetify.VCardText():
                        vuetify.VBtn(color="warning", block=True, class_="mb-2", children="Button 5")
                        vuetify.VBtn(color="error", block=True, children="Button 6")

        # App bar (unchanged)
        with vuetify.VAppBar(app=True):
            vuetify.VAppBarNavIcon(click="leftDrawer = !leftDrawer")
            vuetify.VToolbarTitle("Hello trame")
            vuetify.VSpacer()
            vuetify.VBtn(icon=True, click="rightDrawer = !rightDrawer")
            with vuetify.VIcon():
                vuetify.VIcon("mdi-toolbox")

        # Main content (unchanged)
        with vuetify.VMain():
            with vuetify.VContainer(
                fluid=True,
                classes="pa-0 fill-height",
                style="height: 100vh;",
            ):
                view = vtk.VtkLocalView(renderWindow)
                ctrl.view_reset_camera = view.reset_camera

    # Add these lines to your server setup
    server.state.leftDrawer = True
    server.state.rightDrawer = True
    server.start()

# Start the application
if __name__ == "__main__":
    print("Hello Trame")
    main()   