# backend module for the ampersandCFD project
# Description: This file contains the code for managing project structure and
# generate OpenFOAM files


import yaml
import os
import shutil
from primitives import ampersandPrimitives, ampersandIO
from constants import meshSettings, physicalProperties, numericalSettings, inletValues
from constants import solverSettings, boundaryConditions, simulationSettings
from stlAnalysis import stlAnalysis
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
        self.stl_files = [] # list to store the settings for stl files
        self.stl_names = [] # list to store the names of the stl files

    def set_project_directory(self, project_directory_path):
        if project_directory_path is None:
            ampersandIO.printMessage("No directory selected. Aborting project creation.")
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
            ampersandIO.printMessage("No directory selected. Aborting project creation.")
            return -1
        self.project_path = os.path.join(self.project_directory_path, self.user_name, self.project_name)
        
    # create the project path for the project name
    def create_project_path(self):
        if not self.project_directory_path:
            ampersandIO.printMessage("No directory selected. Aborting project creation.")
            return -1
        self.project_path = os.path.join(self.project_directory_path, self.project_name)

    def check_project_path(self): # check if the project path exists and if the project is already existing
        if os.path.exists(self.project_path):
            settings_file = os.path.join(self.project_path, "project_settings.yaml")
            if os.path.exists(settings_file):
                ampersandIO.printMessage("Project already exists, loading project settings")
                self.existing_project = True
                return 0
            else:
                self.existing_project = False
                return -1
        else:
            self.existing_project = False
            return -1

    # Create the project directory in the specified location.
    # 0, constant, system, constant/triSurface directories are created.
    def create_project(self):
        # check if the project path exists
        if self.project_path is None:
            ampersandIO.printMessage("No project path selected. Aborting project creation.")
            return -1
        if os.path.exists(self.project_path):
            ampersandIO.printMessage("Directory exists")
        else:
            ampersandIO.printMessage("Creating project directory")
            try:
                os.makedirs(self.project_path)
                
            except OSError as error:
                ampersandIO.printError(error)
        try:
            os.chdir(self.project_path)
        except OSError as error:
                ampersandIO.printError(error)
        cwd = os.getcwd()
        ampersandIO.printMessage(f"Working directory: {cwd}")

        # create 0, constant and system directory
        try:
            os.mkdir("0")
            os.mkdir("constant")
            os.mkdir("system")
            os.mkdir("constant/triSurface")
        except OSError as error:
            ampersandIO.printError("File system already exists. Skipping the creation of directories")   
            return -1
        return 0 # return 0 if the project is created successfully 

    # write current settings to the project_settings.yaml file inside the project directory
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

    # If the project is already existing, load the settings from the project_settings.yaml file
    def load_settings(self):
        settings = ampersandPrimitives.yaml_to_dict('project_settings.yaml')
        self.meshSettings = settings['meshSettings']
        self.physicalProperties = settings['physicalProperties']
        self.numericalSettings = settings['numericalSettings']
        self.inletValues = settings['inletValues']
        self.boundaryConditions = settings['boundaryConditions']
        self.solverSettings = settings['solverSettings']
        #self.settings = (self.meshSettings, self.physicalProperties, self.numericalSettings, self.inletValues, self.boundaryConditions)

    # If the project is not existing, load the default settings
    def load_default_settings(self):
        self.meshSettings = meshSettings
        self.physicalProperties = physicalProperties
        self.numericalSettings = numericalSettings
        self.inletValues = inletValues
        self.boundaryConditions = boundaryConditions
        self.simulationSettings = simulationSettings
        self.solverSettings = solverSettings
        #self.settings = (self.meshSettings, self.physicalProperties, 
        #                 self.numericalSettings, self.inletValues, self.boundaryConditions, self.simulationSettings, self.solverSettings)

    # Create the settings for the project or load the existing settings
    def create_settings(self):
        if self.existing_project:
            try:
                self.load_settings()
            except FileNotFoundError:
                ampersandIO.printMessage("Settings file not found. Loading default settings")
                self.load_default_settings()
                self.write_settings()
        else:
            self.load_default_settings()
            self.write_settings()

    # Add a stl file to the project settings (self.meshSettings)
    def add_stl_to_mesh_settings(self, stl_name,refMin=0, refMax=0, featureEdges='true', featureLevel=1, nLayers=1):
        # stl file has the following format: 
        # {'name': 'stl1.stl','type':'triSurfaceMesh', 'refineMin': 1, 'refineMax': 3, 
        #             'featureEdges':'true','featureLevel':3,'nLayers':3}
        stl_ = {'name': stl_name, 'type':'triSurfaceMesh', 'refineMin': refMin, 'refineMax': refMax, 
                'featureEdges':featureEdges, 'featureLevel':featureLevel, 'nLayers':nLayers}
        
        self.stl_names.append(stl_name)
        self.stl_files.append(stl_)
        

    def ask_stl_settings(self,stl_file):
        ampersandIO.printMessage(f"Settings of the {stl_file['name']} file")
        stl_file['refineMin'] = ampersandIO.get_input("Min Refinement: ")
        stl_file['refineMax'] = ampersandIO.get_input("Max Refinement: ")
        featureEdges = ampersandIO.get_input("Refine Feature Edges?: (y/N) ")
        if(featureEdges == 'y'):
            stl_file['featureEdges'] = 'true'
        else:    
            stl_file['featureEdges'] = 'false'
        stl_file['featureLevel'] = ampersandIO.get_input("Feature Level: ")
        stl_file['nLayers'] = ampersandIO.get_input("Number of Layers: ")

    def add_stl_to_project(self):
        for stl_file in self.stl_files:
            #self.ask_stl_settings(stl_file)
            self.meshSettings['geometry'].append(stl_file)

    def add_stl_file(self): # to only copy the STL file to the project directory and add it to the STL list
        stl_file = ampersandPrimitives.ask_for_file([("STL Geometry", "*.stl"), ("OBJ Geometry", "*.obj")])
        if os.path.exists(stl_file):
            # add the stl file to the project
            # This is a bit confusing. 
            # stl_name is the name of the file, stl_file is the path to the file
            file_path_to_token = stl_file.split("/")
            stl_name = file_path_to_token[-1]
            if stl_name in self.stl_names:
                ampersandIO.printMessage(f"STL file {stl_name} already exists in the project")
                return -1
            self.add_stl_to_mesh_settings(stl_name)
            stl_path = os.path.join(self.project_path, "constant", "triSurface", stl_name)
            try:
                ampersandIO.printMessage(f"Copying {stl_name} to the project directory")
                shutil.copy(stl_file, stl_path)
            except OSError as error:
                ampersandIO.printError(error)
                return -1
        else:
            ampersandIO.printMessage("File does not exist. Aborting project creation.")
            return -1
        return 0
            
    
    def list_stl_files(self):
        i = 1
        for stl_file in self.stl_files:
            ampersandIO.printMessage(f"{i}:\t{stl_file['name']}")
            i += 1
     
    def create_project_files(self):
        #(meshSettings, physicalProperties, numericalSettings, inletValues, boundaryConditions)=caseSettings
        # check if the current working directory is the project directory
        if not os.path.exists(self.project_path):
            ampersandIO.printMessage("Project directory does not exist. Aborting project creation.")
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
    project.project_path = "/Users/thawtar/Desktop/ampersand_tests/test6"
    project.create_project()
    project.create_settings()
    yN = ampersandIO.get_input("Add STL file to the project (y/N)?")
    while yN.lower() == 'y':
        project.add_stl_file()
        yN = ampersandIO.get_input("Add another STL file to the project (y/N)?: ")
    project.add_stl_to_project()
    # Before creating the project files, the settings are flushed to the project_settings.yaml file
    project.write_settings()
    project.create_project_files()

if __name__ == '__main__':
    # Specify the output YAML file
    main()
