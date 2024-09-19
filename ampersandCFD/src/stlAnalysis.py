import os
import vtk
import numpy as np
from stlToOpenFOAM import find_inside_point

class stlAnalysis:
    def __init__(self):
        pass

    @staticmethod
    def roundl(x):
        return float(np.around(x,decimals=1))
        

    # to calculate the domain size for blockMeshDict
    @staticmethod
    def calc_domain_size(stlBoundingBox,sizeFactor=1,onGround=False,internalFlow=False):
        stlMinX,stlMaxX,stlMinY,stlMaxY,stlMinZ,stlMaxZ= stlBoundingBox
        # this part is for external flow
        bbX = stlMaxX - stlMinX
        bbY = stlMaxY - stlMinY
        bbZ = stlMaxZ - stlMinZ
        minX = stlMinX - 1.5*bbX*sizeFactor
        maxX = stlMaxX + 5*bbX*sizeFactor
        minY = stlMinY - 3*bbY*sizeFactor
        maxY = stlMaxY + 3*bbY*sizeFactor
        minZ = stlMinZ - 5*bbZ*sizeFactor
        maxZ = stlMaxZ + 5*bbZ*sizeFactor
        
        if(internalFlow):
            minX = stlMinX - 0.1*bbX*sizeFactor
            maxX = stlMaxX + 0.1*bbX*sizeFactor
            minY = stlMinY - 0.1*bbY*sizeFactor
            maxY = stlMaxY + 0.1*bbY*sizeFactor
            minZ = stlMinZ - 0.1*bbZ*sizeFactor
            maxZ = stlMaxZ + 0.1*bbZ*sizeFactor
        """
        if(bbX > 0.1 and bbY > 0.1 and bbZ > 0.1):
            (minX,maxX,minY,maxY,minZ,maxZ) = (np.around(minX,decimals=1),
                                               np.around(maxX,decimals=1),np.around(minY,decimals=1),
                                               np.around(maxY,decimals=1),np.around(minZ,decimals=1),
                                               np.around(maxZ,decimals=1))
        """
        if(bbX > 0.1 and bbY > 0.1 and bbZ > 0.1):
            minX = stlAnalysis.roundl(minX)
            maxX = stlAnalysis.roundl(maxX)
            minY = stlAnalysis.roundl(minY)
            maxY = stlAnalysis.roundl(maxY)
            minZ = stlAnalysis.roundl(minZ)
            maxZ = stlAnalysis.roundl(maxZ)
        if onGround: # the the body is touching the ground
            minZ = stlMinZ
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

    @staticmethod
    def read_stl(stl_file_path):
        # Check if the file exists
        if not os.path.exists(stl_file_path):
            raise FileNotFoundError(f"File not found: {stl_file_path}. Make sure the file exists.")
        # Create a reader for the STL file
        reader = vtk.vtkSTLReader()
        reader.SetFileName(stl_file_path)
        reader.Update()

        # Get the output data from the reader
        poly_data = reader.GetOutput()
        return poly_data


    # to calculate the mesh settings for blockMeshDict and snappyHexMeshDict
    @staticmethod
    def calc_mesh_settings(stlBoundingBox,nu=1e-6,rho=1000.,U=1.0,maxCellSize=0.5,sizeFactor=1.0,onGround=False,internalFlow=False):
        maxSTLLength = stlAnalysis.getMaxSTLDim(stlBoundingBox)
        if(maxCellSize < 0.001):
            maxCellSize = maxSTLLength/4.
        domain_size = stlAnalysis.calc_domain_size(stlBoundingBox=stlBoundingBox,sizeFactor=sizeFactor,onGround=onGround,internalFlow=internalFlow)
        backgroundCellSize = min(maxSTLLength/6.,maxCellSize) # this is the size of largest blockMesh cells
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
        return domain_size, nx, ny, nz, refLevel

    # to set mesh settings for blockMeshDict and snappyHexMeshDict 
    @staticmethod
    def set_mesh_settings(meshSettings, domain_size, nx, ny, nz, refLevel):
        meshSettings['domain'] = {'minx': domain_size[0], 'maxx': domain_size[1], 'miny': domain_size[2], 'maxy': domain_size[3], 'minz': domain_size[4], 'maxz': domain_size[5], 'nx': nx, 'ny': ny, 'nz': nz}
        refMin = max(1,refLevel-2)
        refMax = refLevel
        for geometry in meshSettings['geometry']:
            if geometry['type'] == 'triSurfaceMesh':
                geometry['refineMin'] = refMin
                geometry['refineMax'] = refMax
        return meshSettings
    
    @staticmethod
    def calc_center_of_mass(mesh):
        center_of_mass_filter = vtk.vtkCenterOfMass()
        center_of_mass_filter.SetInputData(mesh)
        center_of_mass_filter.Update()
        center_of_mass = center_of_mass_filter.GetCenter()
        return center_of_mass
    
    @staticmethod
    def analyze_stl(stl_file_path):
        mesh = stlAnalysis.read_stl(stl_file_path)
        bounds = stlAnalysis.compute_bounding_box(stl_file_path)
        stlMinX,stlMaxX,stlMinY,stlMaxY,stlMinZ,stlMaxZ= bounds
        outsideX = stlMaxX + 0.05*(stlMaxX-stlMinX)
        outsideY = (stlMaxY - stlMinY)/2.
        outsideZ = (stlMaxZ - stlMinZ)/2.
        outsidePoint = (outsideX,outsideY,outsideZ)
        center_of_mass = stlAnalysis.calc_center_of_mass(mesh)
        insidePoint = find_inside_point(mesh,center_of_mass,min_bounds=None,max_bounds=None)
        return center_of_mass, insidePoint, outsidePoint
    
    @staticmethod
    def set_mesh_location(meshSettings, stl_file_path, internalFlow=False):
        center_of_mass, insidePoint, outsidePoint = stlAnalysis.analyze_stl(stl_file_path)
        if internalFlow:
            meshSettings['castellatedMeshControls']['locationInMesh'] = [insidePoint[0],insidePoint[1],insidePoint[2]]
        else:
            meshSettings['castellatedMeshControls']['locationInMesh'] = [outsidePoint[0],outsidePoint[1],outsidePoint[2]]
        return meshSettings

if __name__ == "__main__":
    stl_file = "flange.stl"
    stlBoundingBox = stlAnalysis.compute_bounding_box(stl_file)
    fluid_properties = {'rho': 1.225, 'nu': 1.5e-5}
    stlAnalysis.calc_mesh_settings(stlBoundingBox,U=1.0,maxCellSize=0.1)