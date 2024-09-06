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


from events import events
# ---------------------------------------------------------
# This is a test file for the Trame application
# ---------------------------------------------------------

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
    

    with SinglePageWithDrawerLayout(server) as layout:
        layout.title.set_text("Hello trame")
        with layout.content:
            # Second Content Area
            with vuetify.VRow(rows=12):
                
                with vuetify.VCol(cols=12,md=8):
                    
                    with vuetify.VContainer(
                        fluid=True,
                        classes="pa-0 fill-height", #"pa-0 fill-height",
                        style="height: 80vh;",
                    ):
                        view = vtk.VtkLocalView(renderWindow)
                        ctrl.view_reset_camera = view.reset_camera
            
            with vuetify.VRow():
                with vuetify.VCol():
                
                    vuetify.VBtn(
                        color="primary",
                        click=evs.openBtn,
                        children="Close dialog",
                    )
                    vuetify.VBtn(
                        color="primary",
                        click=evs.openBtn,
                        children="Open dialog",
                    )
                    vuetify.VBtn(
                        color="primary",
                        click=evs.openBtn,
                        children="Save",
                    )
            
                       
    server.start()



    # Start the application
if __name__ == "__main__":
    print("Hello Trame")
    main()   