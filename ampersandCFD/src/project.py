# backend module for the ampersandCFD project
from primitives import ampersandPrimitives
# Description: This file contains the code for managing project structure and
# generate OpenFOAM files


import yaml
import os
from primitives import ampersandPrimitives
from constants import meshSettings, physicalProperties, numericalSettings, inletValues
from constants import solverSettings, boundaryConditions, simulationSettings
from blockMeshGenerator import generate_blockMeshDict
from snappyHexMeshGenerator import generate_snappyHexMeshDict
from surfaceExtractor import create_surfaceFeatureExtractDict
from transportAndTurbulence import create_transportPropertiesDict, create_turbulencePropertiesDict
#from transportAndTurbulence import write_transportPropertiesDict, write_turbulencePropertiesDict
from boundaryConditionsGenerator import create_boundary_conditions
from controlDictGenerator import createControlDict
from numericalSettingsGenerator import create_fvSchemesDict, create_fvSolutionDict

#from ../constants/constants import meshSettings


class ampersandProject: # ampersandProject class to handle the project creation and manipulation
    # this class will contain the methods to handle the logic and program flow
    def __init__(self):
        # project path = project_directory_path/user_name/project_name
        self.project_directory_path = None
        self.project_name = None
        self.user_name = None
        self.caseSettings = None
        self.meshSettings = None
        self.physicalProperties = None
        self.numericalSettings = None
        self.simulationSettings = None
        self.solverSettings = None
        self.inletValues = None
        self.boundaryConditions = None
        self.simulationSettings = None
        self.settings = None
        self.project_path = None
        self.existing_project = False # flag to check if the project is already existing

    def set_project_directory(self, project_directory_path):
        if project_directory_path is None:
            print("No directory selected. Aborting project creation.")
            exit()
        assert os.path.exists(project_directory_path), "The chosen directory does not exist"
        self.project_directory_path = project_directory_path

    def set_project_name(self, project_name):
        self.project_name = project_name

    def set_user_name(self, user_name):
        self.user_name = user_name

    # create the project path for the user and project name
    def create_project_path_user(self):
        if not self.project_directory_path:
            print("No directory selected. Aborting project creation.")
            return -1
        self.project_path = os.path.join(self.project_directory_path, self.user_name, self.project_name)
        
    # create the project path for the project name
    def create_project_path(self):
        if not self.project_directory_path:
            print("No directory selected. Aborting project creation.")
            return -1
        self.project_path = os.path.join(self.project_directory_path, self.project_name)

    def check_project_path(self): # check if the project path exists and if the project is already existing
        if os.path.exists(self.project_path):
            settings_file = os.path.join(self.project_path, "project_settings.yaml")
            if os.path.exists(settings_file):
                print("Project already exists, loading project settings")
                self.existing_project = True
                return 0
            else:
                self.existing_project = False
                return -1
        else:
            self.existing_project = False
            return -1


    def create_project(self):
        # check if the project path exists
        if self.project_path is None:
            print("No project path selected. Aborting project creation.")
            return -1
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
            'boundaryConditions': self.boundaryConditions,
            'solverSettings': self.solverSettings,
            'simulationSettings': self.simulationSettings
        }
        ampersandPrimitives.dict_to_yaml(settings, 'project_settings.yaml')

    
    def load_settings(self):
        settings = ampersandPrimitives.yaml_to_dict('project_settings.yaml')
        self.meshSettings = settings['meshSettings']
        self.physicalProperties = settings['physicalProperties']
        self.numericalSettings = settings['numericalSettings']
        self.inletValues = settings['inletValues']
        self.boundaryConditions = settings['boundaryConditions']
        self.solverSettings = settings['solverSettings']
        self.settings = (self.meshSettings, self.physicalProperties, self.numericalSettings, self.inletValues, self.boundaryConditions)

    def load_default_settings(self):
        self.meshSettings = meshSettings
        self.physicalProperties = physicalProperties
        self.numericalSettings = numericalSettings
        self.inletValues = inletValues
        self.boundaryConditions = boundaryConditions
        self.simulationSettings = simulationSettings
        self.solverSettings = solverSettings
        self.settings = (self.meshSettings, self.physicalProperties, 
                         self.numericalSettings, self.inletValues, self.boundaryConditions, self.simulationSettings, self.solverSettings)


    def create_settings(self):
        if self.existing_project:
            self.load_settings()
        else:
            self.load_default_settings()
            self.write_settings()
    
    def create_project_files(self):
        #(meshSettings, physicalProperties, numericalSettings, inletValues, boundaryConditions)=caseSettings
        # check if the current working directory is the project directory
        if not os.path.exists(self.project_path):
            print("Project directory does not exist. Aborting project creation.")
            return -1
        if os.getcwd() != self.project_path:
            os.chdir(self.project_path)
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
        fvSchemesDict = create_fvSchemesDict(self.numericalSettings)
        ampersandPrimitives.write_dict_to_file("fvSchemes", fvSchemesDict)
        fvSolutionDict = create_fvSolutionDict(self.numericalSettings, self.solverSettings)
        ampersandPrimitives.write_dict_to_file("fvSolution", fvSolutionDict)

def main():
    project = ampersandProject()
    #project.set_project_directory(ampersandPrimitives.ask_for_directory())
    #project_name = input("Enter the project name: ")
    #project.set_project_name(project_name)
    #user_name = input("Enter the user name: ")
    #project.set_user_name(user_name)
    #project.create_project_path_user()
    project.project_path = "/Users/thawtar/Desktop/ampersand_tests/test5"
    project.create_project()
    project.create_settings()
    project.create_project_files()

if __name__ == '__main__':
    # Specify the output YAML file
    main()
