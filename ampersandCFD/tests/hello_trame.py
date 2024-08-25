import trame, trame_vtk
from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout,SinglePageLayout
from trame.widgets import vuetify, vtk
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkPolyDataMapper,
)

from events import events
# ---------------------------------------------------------
# This is a test file for the Trame application
# ---------------------------------------------------------

def main():
    # Create the Trame application
    server = get_server(client_type="vue2")
    events = events()
    state, ctrl = server.state, server.controller
    field = vuetify.VTextField(
        label="Weight",
        v_model=("myWeight",28),
        suffix=("currentSuffix","lbs"),
    )
    with SinglePageLayout(server) as layout:
        layout.title.set_text("Hello trame")
        
        with layout.content:
            """with vuetify.VContainer(
                fluid=True,
                classes="pa-0 fill-height",
            ):"""
            vuetify.VBtn(
                color="primary",
                click="openDialog",
                children="Open dialog",
            )
                #view = vtk.VtkLocalView(renderWindow)
                #ctrl.view_reset_camera = view.reset_camera
    server.start()


    # Start the application
if __name__ == "__main__":
    main()   