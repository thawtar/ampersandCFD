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
        maxX = stlMaxX + 7.5*bbX*sizeFactor
        minY = stlMinY - 2.5*bbY*sizeFactor
        maxY = stlMaxY + 2.5*bbY*sizeFactor
        minZ = stlMinZ - 2.5*bbZ*sizeFactor
        maxZ = stlMaxZ + 2.5*bbZ*sizeFactor
        
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
            maxZ = stlMaxZ + 4.0*bbZ*sizeFactor
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
    
    # to calculate the refinement box for snappyHexMeshDict
    @staticmethod
    def getRefinementBox(stlBoundingBox):
        stlMinX,stlMaxX,stlMinY,stlMaxY,stlMinZ,stlMaxZ= stlBoundingBox
        bbX = stlMaxX - stlMinX
        bbY = stlMaxY - stlMinY
        bbZ = stlMaxZ - stlMinZ
        boxMinX = stlMinX - 0.2*bbX
        boxMaxX = stlMaxX + 4.5*bbX
        boxMinY = stlMinY - 1.0*bbY
        boxMaxY = stlMaxY + 1.0*bbY
        boxMinZ = stlMinZ - 1.0*bbZ
        boxMaxZ = stlMaxZ + 1.0*bbZ
        return (boxMinX,boxMaxX,boxMinY,boxMaxY,boxMinZ,boxMaxZ)
    
    @staticmethod
    def getRefinementBoxClose(stlBoundingBox):
        stlMinX,stlMaxX,stlMinY,stlMaxY,stlMinZ,stlMaxZ= stlBoundingBox
        bbX = stlMaxX - stlMinX
        bbY = stlMaxY - stlMinY
        bbZ = stlMaxZ - stlMinZ
        boxMinX = stlMinX + 0.1*bbX
        boxMaxX = stlMaxX + 3*bbX
        boxMinY = stlMinY - 0.45*bbY
        boxMaxY = stlMaxY + 0.45*bbY
        boxMinZ = stlMinZ - 0.45*bbZ
        boxMaxZ = stlMaxZ + 0.45*bbZ
        return (boxMinX,boxMaxX,boxMinY,boxMaxY,boxMinZ,boxMaxZ)
    
    # to add refinement box to mesh settings
    @staticmethod
    def addRefinementBoxToMesh(meshSettings,stl_path,boxName='refinementBox',refLevel=2):
        stlBoundingBox = stlAnalysis.compute_bounding_box(stl_path)
        box = stlAnalysis.getRefinementBox(stlBoundingBox)
        meshSettings['geometry'].append({'name': boxName,'type':'searchableBox', 'purpose':'refinement',
                                         'min': [box[0], box[2], box[4]], 'max': [box[1], box[3], box[5]],
                                         'refineMax': refLevel})
        fineBox = stlAnalysis.getRefinementBoxClose(stlBoundingBox)
        meshSettings['geometry'].append({'name': 'fineBox','type':'searchableBox', 'purpose':'refinement',
                                         'min': [fineBox[0], fineBox[2], fineBox[4]], 'max': [fineBox[1], fineBox[3], fineBox[5]],
                                         'refineMax': refLevel+1})
        return meshSettings

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
        return max_y/thicknessRatio

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
    def calc_mesh_settings(stlBoundingBox,nu=1e-6,rho=1000.,U=1.0,maxCellSize=0.5,sizeFactor=1.0,
                           expansion_ratio=1.2,onGround=False,internalFlow=False,refinement=1,nLayers=5):
        maxSTLLength = stlAnalysis.getMaxSTLDim(stlBoundingBox)
        if(maxCellSize < 0.001):
            maxCellSize = maxSTLLength/4.
        domain_size = stlAnalysis.calc_domain_size(stlBoundingBox=stlBoundingBox,sizeFactor=sizeFactor,onGround=onGround,internalFlow=internalFlow)
        if(refinement==0):
            backgroundCellSize = min(maxSTLLength/4.,maxCellSize) # this is the size of largest blockMesh cells
            target_yPlus = 200
            nLayers = 3
        elif(refinement==1):
            backgroundCellSize = min(maxSTLLength/8.,maxCellSize)
            target_yPlus = 100
            nLayers = 5
        elif(refinement==2):
            target_yPlus = 50
            nLayers = 5
            backgroundCellSize = min(maxSTLLength/12.,maxCellSize)
        else:
            backgroundCellSize = min(maxSTLLength/8.,maxCellSize) # medium setting for default
            target_yPlus = 100
        nx,ny,nz = stlAnalysis.calc_nx_ny_nz(domain_size,backgroundCellSize)
        L = maxSTLLength # this is the characteristic length to be used in Re calculations
        target_y = stlAnalysis.calc_y(nu,rho,L,U,target_yPlus=target_yPlus) # this is the thickness of closest cell
        targetCellSize = stlAnalysis.calc_cell_size(target_y,expRatio=expansion_ratio,thicknessRatio=0.3,nLayers=nLayers)
        refLevel = stlAnalysis.calc_refinement_levels(backgroundCellSize,targetCellSize)
        # adjust refinement levels based on coarse, medium, fine settings
        if(refinement==0):
            refLevel = max(1,refLevel+1)
        elif(refinement==1):
            refLevel = max(2,refLevel+2)
        elif(refinement==2):
            refLevel = max(3,refLevel+3)
        else:
            refLevel = max(2,refLevel)
        minVolumeSize = backgroundCellSize**3/(8.**refLevel*20.)
        # print the summary of results
        print(f"Domain size {domain_size}")
        print(f"Simple grading: {nx},{ny},{nz}")
        print(f"Max cell size: {backgroundCellSize}")
        print(f"Max volume size: {backgroundCellSize**3}")
        print(f"Min volume size: {minVolumeSize}")
        print(f"Target Y:{target_y}")
        print(f"Refinement Level:{refLevel}")
        return domain_size, nx, ny, nz, refLevel,target_y,minVolumeSize
    
    @staticmethod
    def set_layer_thickness(meshSettings,thickness=0.01):
        meshSettings['addLayersControls']['finalLayerThickness'] = thickness
        minThickness = max(0.0001,thickness/100.)
        meshSettings['addLayersControls']['minThickness'] = minThickness
        return meshSettings
    
    @staticmethod
    def set_min_vol(meshSettings,minVol=1e-15):
        meshSettings['meshQualityControls']['minVol'] = 1e-15 #minVol/100.
        return meshSettings

    # to set mesh settings for blockMeshDict and snappyHexMeshDict 
    @staticmethod
    def set_mesh_settings(meshSettings, domain_size, nx, ny, nz, refLevel,featureLevel=1):
        meshSettings['domain'] = {'minx': domain_size[0], 'maxx': domain_size[1], 'miny': domain_size[2], 'maxy': domain_size[3], 'minz': domain_size[4], 'maxz': domain_size[5], 'nx': nx, 'ny': ny, 'nz': nz}
        refMin = max(2,refLevel-2)
        refMax = max(3,refLevel)
        for geometry in meshSettings['geometry']:
            if geometry['type'] == 'triSurfaceMesh':
                geometry['refineMin'] = refMin
                geometry['refineMax'] = refMax
                #geometry['featureEdges'] = 'true'
                geometry['featureLevel'] = featureLevel
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
    
    @staticmethod
    def set_stl_solid_name(stl_file='input.stl'):
        print(f"Setting solid name for {stl_file}")
        # if the file does not exist, return -1
        if not os.path.exists(stl_file):
            print(f"File not found: {stl_file}")
            return -1
        # if exists, extract file name by removing the directory path
        new_lines = []
        new_stl_file = stl_file[:-4] + ".stl"
        solid_name = os.path.basename(stl_file)[:-4]
        #print(f"Solid name: {solid_name}")
        # open the file
        try:
            with open(stl_file,'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"File not found: {stl_file}")
            return -1
        # find the solid name
        for line in lines:
            if 'endsolid' in line:
                # replace the solid name using above solid_name
                line = f"endsolid {solid_name}\n"
            # replace the endsolid name
            elif 'solid' in line:
                line = f"solid {solid_name}\n"
            else:
                pass
            new_lines.append(line)
        #print(f"Solid name: {solid_name}")
        # write the new lines to the file
        try:
            with open(new_stl_file,'w') as f:
                f.writelines(new_lines)
        except FileNotFoundError:
            print(f"File not found: {new_stl_file}")
            return -1
        return 0

def main():
    stl_file = "/Users/thawtar/Desktop/CFD_Monkey/STL/flange.stl"
    stlAnalysis.set_stl_solid_name(stl_file)

if __name__ == "__main__":
    main()