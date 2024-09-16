import os
import vtk
import numpy as np

class stlAnalysis:
    def __init__(self):
        pass

    # to calculate the domain size for blockMeshDict
    @staticmethod
    def calc_domain_size(stlBoundingBox,sizeFactor=1):
        stlMinX,stlMaxX,stlMinY,stlMaxY,stlMinZ,stlMaxZ= stlBoundingBox
        bbX = stlMaxX - stlMinX
        bbY = stlMaxY - stlMinY
        bbZ = stlMaxZ - stlMinZ
        minX = stlMinX - 2*bbX*sizeFactor
        maxX = stlMaxX + 7*bbX*sizeFactor
        minY = stlMinY - 3*bbY*sizeFactor
        maxY = stlMaxY + 3*bbY*sizeFactor
        minZ = stlMinZ - 5*bbZ*sizeFactor
        maxZ = stlMaxZ + 5*bbZ*sizeFactor
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
    def calc_y(nu=1e-6,rho=1000.,L=1.0,u=1.0,target_yPlus=200):
        #rho = fluid_properties['rho']
        #nu = fluid_properties['nu']
        Re = u*L/nu
        Cf = 0.0592*Re**(-1./5.)
        tau = 0.5*rho*Cf*u**2.
        uStar = np.sqrt(tau/rho)
        y = target_yPlus*nu/uStar
        return y

    # calculate nearest cell size for a given expansion ratio and layer count
    @staticmethod
    def calc_cell_size(y_=0.001,nLayers=5,expRatio=1.2,thicknessRatio=0.3):
        max_y = y_*expRatio**(nLayers)
        return max_y*thicknessRatio

    @staticmethod
    def calc_refinement_levels(max_cell_size=0.1,target_cell_size=0.001):
        size_ratio = max_cell_size / target_cell_size
        n = np.log(size_ratio)/np.log(2.)
        #print(n)
        return int(np.ceil(n))

    @staticmethod
    def calc_nx_ny_nz(domain_size,target_cell_size):
        (minX,maxX,minY,maxY,minZ,maxZ) = domain_size
        nx = (maxX-minX)/target_cell_size
        ny = (maxY-minY)/target_cell_size
        nz = (maxZ-minZ)/target_cell_size
        nx, ny, nz = int(nx), int(ny), int(nz)
        return (nx,ny,nz)

    @staticmethod
    def set_mesh_settings(stlBoundingBox,nu=1e-6,rho=1000.,U=1.0,maxCellSize=0.1):
        domain_size = stlAnalysis.calc_domain_size(stlBoundingBox=stlBoundingBox)
        maxSTLLength = stlAnalysis.getMaxSTLDim(stlBoundingBox)
        backgroundCellSize = min(maxSTLLength/4.,maxCellSize) # this is the size of largest blockMesh cells
        nx,ny,nz = stlAnalysis.calc_nx_ny_nz(domain_size,backgroundCellSize)
        L = maxSTLLength # this is the characteristic length to be used in Re calculations
        target_y = stlAnalysis.calc_y(nu,rho,L,U,target_yPlus=200) # this is the thickness of closest cell
        targetCellSize = stlAnalysis.calc_cell_size(target_y,expRatio=1.3,thicknessRatio=0.4)
        refLevel = stlAnalysis.calc_refinement_levels(backgroundCellSize,targetCellSize)
        # print the summary of results
        print(f"Domain size {domain_size}")
        print(f"Simple grading: {nx},{ny},{nz}")
        print(f"Target Y:{target_y}")
        print(f"Refinement Level:{refLevel}")

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
        # xmin, xmax, ymin, ymax, zmin, zmax = bounds
        # Optionally, return the bounding box as a tuple
        return bounds

if __name__ == "__main__":
    stl_file = "flange.stl"
    stlBoundingBox = stlAnalysis.compute_bounding_box(stl_file)
    fluid_properties = {'rho': 1.225, 'nu': 1.5e-5}
    stlAnalysis.set_mesh_settings(stlBoundingBox,U=1.0,maxCellSize=0.1)