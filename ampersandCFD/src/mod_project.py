import os
import shutil
from headers import get_ampersand_header
from primitives import ampersandPrimitives, ampersandIO, ampersandDataInput
from constants import meshSettings, physicalProperties, numericalSettings, inletValues
from constants import solverSettings, boundaryConditions, simulationSettings
from constants import simulationFlowSettings, parallelSettings, postProcessSettings
from stlAnalysis import stlAnalysis



# A collection of functions that are used to modify the project
class mod_project:
    def __init__(self):
        pass

    @staticmethod
    def ask_domain_size():
        ampersandIO.printMessage("Domain size is the size of the computational domain in meters")
        minX,minY,minZ = ampersandIO.get_input_vector("Xmin Ymin Zmin: ")
        maxX,maxY,maxZ = ampersandIO.get_input_vector("Xmax Ymax Zmax: ")
        # check if the values are valid
        if(minX>=maxX or minY>=maxY or minZ>=maxZ):
            ampersandIO.printMessage("Invalid domain size, please enter the values again")
            mod_project.ask_domain_size()
        return minX,maxX,minY,maxY,minZ,maxZ

    @staticmethod
    def change_refinement_level(meshSettings):
        refLevels = ["coarse","medium","fine"]
        ampersandIO.printMessage("Current refinement level: "+refLevels[meshSettings['fineLevel']])
        #ampersandIO.printMessage("Refinement level is the number of cells in the smallest direction")
        refinementLevel = ampersandIO.get_input_int("Enter new refinement level (0:coarse, 1:medium, 2:fine): ")
        if(refinementLevel<0 or refinementLevel>2):
            ampersandIO.printMessage("Invalid refinement level, please enter the value again")
            mod_project.change_refinement_level(meshSettings)
        meshSettings['fineLevel'] = refinementLevel
        return meshSettings
    
    @staticmethod
    def change_mesh_size(meshSettings, cellSize):
        minX = meshSettings['domain']["minx"]
        maxX = meshSettings['domain']["maxx"]
        minY = meshSettings['domain']["miny"]
        maxY = meshSettings['domain']["maxy"]
        minZ = meshSettings['domain']["minz"]
        maxZ = meshSettings['domain']["maxz"]
        domain = (minX,maxX,minY,maxY,minZ,maxZ)
        nx,ny,nz = stlAnalysis.calc_nx_ny_nz(domain,cellSize)
        meshSettings['domain']['nx'] = nx
        meshSettings['domain']['ny'] = ny
        meshSettings['domain']['nz'] = nz
        return meshSettings

    @staticmethod
    def change_fluid_properties(physicalProperties):
        ampersandIO.printMessage("Current fluid properties")
        ampersandIO.printMessage(f"Density: {physicalProperties['rho']}")
        ampersandIO.printMessage(f"Kinematic viscosity: {physicalProperties['nu']}")
        physicalProperties['rho'] = ampersandIO.get_input_float("Enter new density (kg/m^3): ")
        physicalProperties['nu'] = ampersandIO.get_input_float("Enter new kinematic viscosity (m^2/s): ")
        # check if the values are valid
        if(physicalProperties['rho']<=0 or physicalProperties['nu']<=0):
            ampersandIO.printMessage("Invalid fluid properties, please enter the values again")
            mod_project.change_fluid_properties(physicalProperties)
        return physicalProperties
        


# this is to test the mod_project class
if __name__ == "__main__":
    project = mod_project()
    project.ask_domain_size()