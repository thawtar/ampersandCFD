# this is to host 3D objects in web browser

from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vtk

# Create a Trame server
server = get_server()
state, ctrl = server.state, server.controller

# Create a VTK rendering component
with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text("3D Object Hosting with Trame")

    # Add a VTK view
    with layout.content:
        view = vtk.VtkRemoteView()
        view.update()

# Define a VTK pipeline
@state.change("trame_ready")
def initialize_vtk(**kwargs):
    from vtkmodules.vtkFiltersSources import vtkSphereSource

    # Create a sphere
    sphere = vtkSphereSource()
    sphere.SetCenter(0, 0, 0)
    sphere.SetRadius(0.5)
    sphere.Update()

    # Send the sphere to the client for rendering
    view.update(sphere.GetOutputPort())

# Start the server
if __name__ == "__main__":
    server.start()
