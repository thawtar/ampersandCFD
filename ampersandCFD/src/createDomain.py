import os
import vtk
import numpy as np

class createDomain:
    def __init__(self) -> None:
        pass

    # to calculate the domain size based on the bounding box of the STL
    @staticmethod
    def calcDomainSize(stlBoundingBox):
        stlMinX,stlMaxX,stlMinY,stlMaxY,stlMinZ,stlMaxZ= stlBoundingBox
        bbX = stlMaxX - stlMinX
        bbY = stlMaxY - stlMinY
        bbZ = stlMaxZ - stlMinZ
        minX = stlMinX - 2*bbX
        maxX = stlMaxX + 7*bbX
        minY = stlMinY - 3*bbY
        maxY = stlMaxY + 3*bbY
        minZ = stlMinZ - 5*bbZ
        maxZ = stlMaxZ + 5*bbZ
        domain_size = (minX,maxX,minY,maxY,minZ,maxZ)
        return domain_size

    # to calculate the max length of STL
    @staticmethod
    def getMaxSTLDim(stlBoundingBox):
        stlMinX,stlMaxX,stlMinY,stlMaxY,stlMinZ,stlMaxZ= stlBoundingBox
        bbX = stlMaxX - stlMinX
        bbY = stlMaxY - stlMinY
        bbZ = stlMaxZ - stlMinZ
        return max(bbX,bbY,bbZ)

    # to calculate the min size of stl
    @staticmethod
    def getMinSTLDim(stlBoundingBox):
        stlMinX,stlMaxX,stlMinY,stlMaxY,stlMinZ,stlMaxZ= stlBoundingBox
        bbX = stlMaxX - stlMinX
        bbY = stlMaxY - stlMinY
        bbZ = stlMaxZ - stlMinZ
        return min(bbX,bbY,bbZ)

    # to calculate nearest wall thickness for a target yPlus value
    @staticmethod
    def calcY(fluid_properties,L=1.0,u=1.0,target_yPlus=200):
        rho = fluid_properties['rho']
        nu = fluid_properties['nu']
        Re = u*L/nu
        Cf = 0.0592*Re**(-1./5.)
        tau = 0.5*rho*Cf*u**2.
        uStar = np.sqrt(tau/rho)
        y = target_yPlus*nu/uStar
        return y

    # calculate nearest cell size for a given expansion ratio and layer count
    @staticmethod
    def calcCellSize(y_=0.001,nLayers=5,expRatio=1.2,thicknessRatio=0.3):
        max_y = y_*expRatio**(nLayers)
        return max_y*thicknessRatio

    # calculate the number of refinement levels
    @staticmethod
    def calcRefinementLevels(max_cell_size=0.1,target_cell_size=0.001):
        size_ratio = max_cell_size / target_cell_size
        n = np.log(size_ratio)/np.log(2.)
        #print(n)
        return int(np.ceil(n))

    # calculate the number of cells in x,y,z directions
    @staticmethod
    def calcNxNyNz(domain_size,target_cell_size):
        (minX,maxX,minY,maxY,minZ,maxZ) = domain_size
        nx = (maxX-minX)/target_cell_size
        ny = (maxY-minY)/target_cell_size
        nz = (maxZ-minZ)/target_cell_size
        nx, ny, nz = int(nx), int(ny), int(nz)
        return (nx,ny,nz)

    # set mesh settings
    @staticmethod
    def setMeshSettings(meshSettings,stlBoundingBox,fluid_properties,U=1.0,maxCellSize=0.1):
        domain_size = createDomain.calcDomainSize(stlBoundingBox=stlBoundingBox)
        maxSTLLength = createDomain.getMaxSTLDim(stlBoundingBox)
        backgroundCellSize = min(maxSTLLength/4.,maxCellSize) # this is the size of largest blockMesh cells
        nx,ny,nz = createDomain.calcNxNyNz(domain_size,backgroundCellSize)
        L = maxSTLLength # this is the characteristic length to be used in Re calculations
        target_y = createDomain.calcY(fluid_properties,L,U,target_yPlus=200) # this is the thickness of closest cell
        targetCellSize = createDomain.calcCellSize(target_y,expRatio=1.3,thicknessRatio=0.4)
        refLevel = createDomain.calcRefinementLevels(backgroundCellSize,targetCellSize)

        # print the summary of results
        print(f"Domain size {domain_size}")
        print(f"Simple grading: {nx},{ny},{nz}")
        print(f"Target Y:{target_y}")
        print(f"Refinement Level:{refLevel}")
        meshSettings['domain']['minx'] = domain_size[0]
        meshSettings['domain']['maxx'] = domain_size[1]
        meshSettings['domain']['miny'] = domain_size[2]
        meshSettings['domain']['maxy'] = domain_size[3]
        meshSettings['domain']['minz'] = domain_size[4]
        meshSettings['domain']['maxz'] = domain_size[5]
        meshSettings['domain']['nx'] = nx
        meshSettings['domain']['ny'] = ny
        meshSettings['domain']['nz'] = nz
        for a in meshSettings['geometry']:
            if a['type'] == 'triSurfaceMesh':
                a['refineMin'] = 1
                a['refineMax'] = refLevel
        return meshSettings
        

    # Function to read STL file and compute bounding box
    @staticmethod
    def compute_bounding_box(stl_file_path):
        # Check if the file exists
        if not os.path.exists(stl_file_path):
            raise FileNotFoundError(f"File not found: {stl_file_path}. Make sure the file exists.")
        # Create a reader for the STL file
        reader = vtk.vtkSTLReader()
        reader.SetFileName(stl_file_path)
        reader.Update()
        # Get the output data from the reader
        poly_data = reader.GetOutput()

        # Calculate the bounding box
        bounds = poly_data.GetBounds()
        return bounds

    # Function to read an STL file
    @staticmethod
    def read_stl(stl_file_path):
        reader = vtk.vtkSTLReader()
        reader.SetFileName(stl_file_path)
        reader.Update()
        return reader.GetOutput()

    # Function to check if a point is inside the STL geometry
    @staticmethod
    def is_point_inside(stl_geometry, point):
        enclosed_points = vtk.vtkSelectEnclosedPoints()
        enclosed_points.SetInputData(vtk.vtkPolyData())
        enclosed_points.SetSurfaceData(stl_geometry)
        enclosed_points.SetTolerance(1e-6)  # Tolerance for considering points close to the surface
        enclosed_points.CheckSurfaceOn()
        enclosed_points.Update()
        enclosed_points.Initialize(vtk.vtkIdList())
        is_inside = enclosed_points.IsInsideSurface(point[0], point[1], point[2])
        return is_inside
