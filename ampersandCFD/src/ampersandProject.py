# backend module for the ampersandCFD project
# Description: This file contains the code to generate OpenFOAM files


import yaml
import os
from primitives import ampersandPrimitives
from constants import meshSettings
from constants import meshSettings, physicalProperties, numericalSettings, inletValues
from constants import boundaryConditions, simulationSettings
from blockMeshGenerator import generate_blockMeshDict
from snappyHexMeshGenerator import generate_snappyHexMeshDict
from surfaceExtractor import create_surfaceFeatureExtractDict
from transportAndTurbulence import create_transportPropertiesDict, create_turbulencePropertiesDict
#from transportAndTurbulence import write_transportPropertiesDict, write_turbulencePropertiesDict
from boundaryConditionsGenerator import create_boundary_conditions
from controlDictGenerator import createControlDict
from tkinter import filedialog, Tk
#from ../constants/constants import meshSettings


class ampersandProject: # ampersandProject class to handle the project creation and manipulation
    # this class will contain the methods to handle the logic and program flow
    def __init__(self):
        self.project_path = None
        self.project_name = None
        self.user_name = None
        self.caseSettings = None
        self.meshSettings = None
        self.physicalProperties = None
        self.numericalSettings = None
        self.inletValues = None
        self.boundaryConditions = None
        self.simulationSettings = None
        self.settings = None
        self.project_path = None
    def set_project_path(self, project_path):
        self.project_path = project_path

    def set_project_name(self, project_name):
        self.project_name = project_name

    def set_user_name(self, user_name):
        self.user_name = user_name


    def create_project_directory(self):
        if os.path.exists(self.project_path):
            print("Directory exists")
        else:
            print("Creating project directory")
            try:
                os.makedirs(self.project_path)
                
            except OSError as error:
                print(error)
        try:
            os.chdir(self.project_path)
        except OSError as error:
                print(error)
        cwd = os.getcwd()
        print(f"Working directory: {cwd}")

        # create 0, constant and system directory
        try:
            os.mkdir("0")
            os.mkdir("constant")
            os.mkdir("system")
        except OSError as error:
            print("File system already exists. Skipping the creation of directories")   
            return -1
        return 0 # return 0 if the project is created successfully 

   
    def write_settings(self):
        settings = {
            'meshSettings': self.meshSettings,
            'physicalProperties': self.physicalProperties,
            'numericalSettings': self.numericalSettings,
            'inletValues': self.inletValues,
            'boundaryConditions': self.boundaryConditions
        }
        ampersandPrimitives.dict_to_yaml(settings, 'project_settings.yaml')

    
    def load_settings(self):
        settings = ampersandPrimitives.yaml_to_dict('project_settings.yaml')
        self.meshSettings = settings['meshSettings']
        self.physicalProperties = settings['physicalProperties']
        self.numericalSettings = settings['numericalSettings']
        self.inletValues = settings['inletValues']
        self.boundaryConditions = settings['boundaryConditions']
        self.settings = (self.meshSettings, self.physicalProperties, self.numericalSettings, self.inletValues, self.boundaryConditions)
        #return self.settings
    
    @staticmethod
    def ask_for_directory():
        root = Tk()
        root.withdraw()  # Hide the main window
        directory = filedialog.askdirectory(title="Select Project Directory")
        return directory if directory else None


    @staticmethod
    def create_project_path_user(proj_path,project_name="testProject", user_name="user1"):
        if not proj_path:
            print("No directory selected. Aborting project creation.")
            return -1

        project_path = os.path.join(proj_path, user_name, project_name)
        print(project_path)
        return project_path

    
    
    def create_project_path(self):
        if not self.project_path:
            print("No directory selected. Aborting project creation.")
            return -1
        self.project_path = os.path.join(self.project_path, self.project_name)


    def create_project_files(self):
        #(meshSettings, physicalProperties, numericalSettings, inletValues, boundaryConditions)=caseSettings
        
        # go inside the constant directory
        os.chdir("constant")
        # create transportProperties file
        tranP = create_transportPropertiesDict(self.physicalProperties)
        # create turbulenceProperties file
        turbP = create_turbulencePropertiesDict(self.physicalProperties)
        ampersandPrimitives.write_dict_to_file("transportProperties", tranP)
        ampersandPrimitives.write_dict_to_file("turbulenceProperties", turbP)
        # go back to the main directory
        os.chdir("..")
        # go inside the 0 directory
        os.chdir("0")
        # create the initial conditions file
        create_boundary_conditions(self.meshSettings, self.boundaryConditions, self.inletValues)    
        # go back to the main directory 
        os.chdir("..")
        # go inside the system directory
        os.chdir("system")
        # create the controlDict file
        controlDict = createControlDict(simulationSettings)
        ampersandPrimitives.write_dict_to_file("controlDict", controlDict)
        blockMeshDict = generate_blockMeshDict(self.meshSettings)
        ampersandPrimitives.write_dict_to_file("blockMeshDict", blockMeshDict)
        snappyHexMeshDict = generate_snappyHexMeshDict(self.meshSettings)
        ampersandPrimitives.write_dict_to_file("snappyHexMeshDict", snappyHexMeshDict)
        surfaceFeatureExtractDict = create_surfaceFeatureExtractDict(self.meshSettings)
        ampersandPrimitives.write_dict_to_file("surfaceFeatureExtractDict", surfaceFeatureExtractDict)


if __name__ == '__main__':
    # Specify the output YAML file
    pass
