# backend module for the ampersandCFD project
# Description: This file contains the code for managing project structure and
# generate OpenFOAM files


import yaml
import os
import shutil
from headers import get_ampersand_header
from primitives import ampersandPrimitives, ampersandIO, ampersandDataInput
from constants import meshSettings, physicalProperties, numericalSettings, inletValues
from constants import solverSettings, boundaryConditions, simulationSettings
from constants import simulationFlowSettings, parallelSettings
from stlAnalysis import stlAnalysis
from blockMeshGenerator import generate_blockMeshDict
from decomposeParGenerator import createDecomposeParDict
from snappyHexMeshGenerator import generate_snappyHexMeshDict
from surfaceExtractor import create_surfaceFeatureExtractDict
from transportAndTurbulence import create_transportPropertiesDict, create_turbulencePropertiesDict
#from transportAndTurbulence import write_transportPropertiesDict, write_turbulencePropertiesDict
from boundaryConditionsGenerator import create_boundary_conditions
from controlDictGenerator import createControlDict
from numericalSettingsGenerator import create_fvSchemesDict, create_fvSolutionDict
from scriptGenerator import ScriptGenerator

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
        self.simulationFlowSettings = None
        self.parallelSettings = None
        self.settings = None
        self.project_path = None
        self.existing_project = False # flag to check if the project is already existing
        self.stl_files = [] # list to store the settings for stl files
        self.stl_names = [] # list to store the names of the stl files
        self.internalFlow = False # default is external flow
        self.onGround = False # default is off the ground
        self.parallel = True # default is parallel simulation
        self.snap = True # default is to use snappyHexMesh
        self.transient = False # default is steady state
        self.refinement = 0 # 0: coarse, 1: medium, 2: fine
        self.characteristicLength = None # default characteristic length

    def remove_duplicate_stl_files(self):
        # detect duplicate dictionaries in the list
        seen = set()
        new_list = []
        for d in self.stl_files:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_list.append(d)
        self.stl_files = new_list

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
            ampersandIO.printMessage("Project already exists. Skipping the creation of directories")
            self.existing_project = True
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
            'simulationSettings': self.simulationSettings,
            'parallelSettings': self.parallelSettings,
            'simulationFlowSettings': self.simulationFlowSettings,
        }
        #print(self.meshSettings)
        ampersandIO.printMessage("Writing settings to project_settings.yaml")
        ampersandPrimitives.dict_to_yaml(settings, 'project_settings.yaml')

    # If the project is already existing, load the settings from the project_settings.yaml file
    def load_settings(self):
        ampersandIO.printMessage("Loading project settings")
        settings = ampersandPrimitives.yaml_to_dict('project_settings.yaml')
        self.meshSettings = settings['meshSettings']
        self.physicalProperties = settings['physicalProperties']
        self.numericalSettings = settings['numericalSettings']
        self.inletValues = settings['inletValues']
        self.boundaryConditions = settings['boundaryConditions']
        self.solverSettings = settings['solverSettings']
        self.simulationSettings = settings['simulationSettings']
        self.parallelSettings = settings['parallelSettings']
        self.simulationFlowSettings = settings['simulationFlowSettings']
        for geometry in self.meshSettings['geometry']:
            if(geometry['type']=='triSurfaceMesh'):
                if(geometry['name'] in self.stl_names):
                    ampersandIO.printMessage(f"STL file {geometry['name']} already exists in the project, skipping the addition")
                else:
                    self.stl_files.append(geometry)
                    self.stl_names.append(geometry['name'])
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
        self.parallelSettings = parallelSettings
        self.simulationFlowSettings = simulationFlowSettings
        #self.settings = (self.meshSettings, self.physicalProperties, 
        #                 self.numericalSettings, self.inletValues, self.boundaryConditions, self.simulationSettings, self.solverSettings)

    # Create the settings for the project or load the existing settings
    def create_settings(self):
        if self.existing_project:
            ampersandIO.printMessage("Project already exists. Loading project settings")
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
    def add_stl_to_mesh_settings(self, stl_name,refMin=0, refMax=0, featureEdges='true', featureLevel=1,purpose='wall'):
        # stl file has the following format: 
        # {'name': 'stl1.stl','type':'triSurfaceMesh','purpose':'wall' ,'refineMin': 1, 'refineMax': 3, 
        #             'featureEdges':'true','featureLevel':3,'nLayers':3}
        #featureLevel = refMax
        # Purpose is wall by default
        # Other purposes are patch, refinementRegion, refinementSurface, cellZone 
        if self.refinement == 0:
            nLayers = 3
        elif self.refinement == 1:
            nLayers = 5
        else:
            nLayers = 7
        stl_ = {'name': stl_name, 'type':'triSurfaceMesh','purpose':purpose, 'refineMin': refMin, 'refineMax': refMax, 
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
        self.remove_duplicate_stl_files()

    def add_stl_file(self): # to only copy the STL file to the project directory and add it to the STL list
        stl_file = ampersandPrimitives.ask_for_file([("STL Geometry", "*.stl"), ("OBJ Geometry", "*.obj")])
        if stl_file is None:
            ampersandIO.printMessage("No file selected. Please select STL file if necessary.")
            return -1
        if os.path.exists(stl_file):
            # add the stl file to the project
            # This is a bit confusing. 
            # stl_name is the name of the file, stl_file is the path to the file
            file_path_to_token = stl_file.split("/")
            stl_name = file_path_to_token[-1]
            if stl_name in self.stl_names:
                ampersandIO.printMessage(f"STL file {stl_name} already exists in the project")
                return -1
            else: # this is to prevent the bug of having the same file added multiple times
                self.add_stl_to_mesh_settings(stl_name)
            # this is the path to the constant/triSurface inside project directory where STL will be copied
            stl_path = os.path.join(self.project_path, "constant", "triSurface", stl_name)
            try:
                ampersandIO.printMessage(f"Copying {stl_name} to the project directory")
                shutil.copy(stl_file, stl_path)
            except OSError as error:
                ampersandIO.printError(error)
                return -1
            try:
                stlAnalysis.set_stl_solid_name(stl_path)
            except Exception as error:
                ampersandIO.printError(error)
                return -1
        else:
            ampersandIO.printMessage("File does not exist. Aborting project creation.")
            return -1
        return 0
            
    
    def list_stl_files(self):
        i = 1
        ampersandIO.printMessage("STL Files in the project:")
        for stl_file in self.stl_files:
            ampersandIO.printMessage(f"{i}:\t{stl_file['name']}")
            i += 1

    def remove_stl_file(self,stl_file_number=0):
        #self.list_stl_files()
        stl_file_number = ampersandIO.get_input("Enter the number of the file to remove: ")
        try:
            stl_file_number = int(stl_file_number)
        except ValueError:
            ampersandIO.printMessage("Invalid input. Aborting operation")
            return -1
        if stl_file_number < 0 or stl_file_number > len(self.stl_files):
            ampersandIO.printMessage("Invalid file number. Aborting operation")
            return -1
        stl_file = self.stl_files[stl_file_number]
        stl_name = stl_file['name']
        self.stl_files.remove(stl_file)
        self.stl_names.remove(stl_name)
        stl_path = os.path.join(self.project_path, "constant", "triSurface", stl_name)
        try:
            os.remove(stl_path)
        except OSError as error:
            ampersandIO.printError(error)
            return -1
        return 0

    def ask_flow_type(self):
        flow_type = ampersandIO.get_input("Internal or External Flow (I/E)?: ")
        if flow_type.lower() == 'i':
            self.internalFlow = True
        else:
            self.internalFlow = False


    def analyze_stl_file(self,stl_file_number=0):
        rho = self.physicalProperties['rho']
        nu = self.physicalProperties['nu']
        U = max(self.inletValues['U'])
        ER = self.meshSettings['addLayersControls']['expansionRatio']
        try:
            stl_file_number = int(stl_file_number)
        except ValueError:
            ampersandIO.printMessage("Invalid input. Aborting operation")
            return -1
        if stl_file_number < 0 or stl_file_number > len(self.stl_files):
            ampersandIO.printMessage("Invalid file number. Aborting operation")
            return -1
        stl_file = self.stl_files[stl_file_number]
        stl_name = stl_file['name']
        print(f"Analyzing {stl_name}")
        stl_path = os.path.join(self.project_path, "constant", "triSurface", stl_name)
        stlBoundingBox = stlAnalysis.compute_bounding_box(stl_path)
        domain_size, nx, ny, nz, refLevel,target_y,minVol = stlAnalysis.calc_mesh_settings(stlBoundingBox, nu, rho,U=U,maxCellSize=2.0,expansion_ratio=ER,
                                                                           onGround=self.onGround,internalFlow=self.internalFlow,
                                                                           refinement=self.refinement)
        featureLevel = max(refLevel+1,1)
        self.meshSettings = stlAnalysis.set_mesh_settings(self.meshSettings, domain_size, nx, ny, nz, refLevel, featureLevel) 
        self.meshSettings = stlAnalysis.set_mesh_location(self.meshSettings, stl_path)
        refinementBoxLevel = max(2,refLevel-3)
        self.meshSettings = stlAnalysis.addRefinementBoxToMesh(self.meshSettings, stl_path,refLevel=refinementBoxLevel)
        #self.meshSettings = stlAnalysis.set_layer_thickness(self.meshSettings, target_y)
        self.meshSettings = stlAnalysis.set_min_vol(self.meshSettings, minVol)
        return 0
    
    def set_inlet_values(self):
        U = ampersandDataInput.get_inlet_values()
        self.inletValues['U'] = U
        self.boundaryConditions['velocityInlet']['u_value'] = U

    def set_fluid_properties(self):
        fluid = ampersandDataInput.choose_fluid_properties()
        if fluid == -1:
            rho, nu = ampersandDataInput.get_physical_properties()
            fluid = {'rho':rho, 'nu':nu}
        self.physicalProperties['rho'] = fluid['rho']
        self.physicalProperties['nu'] = fluid['nu']

    def set_transient(self):
        self.transient = ampersandIO.get_input_bool("Transient simulation (y/N)?: ")

    def set_parallel(self):
        n_core = ampersandIO.get_input_int("Number of cores for parallel simulation: ")
        self.parallelSettings['numberOfSubdomains'] = n_core
    
    
    def set_transient_settings(self):
        if self.transient:
            ampersandIO.printMessage("Transient simulation settings")
            self.simulationSettings['endTime'] = ampersandIO.get_input_float("End time: ")
            self.simulationSettings['writeInterval'] = ampersandIO.get_input_float("Write interval: ")
            self.simulationSettings['deltaT'] = ampersandIO.get_input_float("Time step: ")
            self.simulationSettings['adjustTimeStep'] = 'yes'
            self.simulationSettings['maxCo'] = 0.9
            

    def ask_ground_type(self):
        ground_type = ampersandIO.get_input("Is the ground touching the body (y/N): ")
        if ground_type.lower() == 'y':
            self.onGround = True
        else:
            self.onGround = False

    def ask_refinement_level(self):
        self.refinement = ampersandDataInput.get_mesh_refinement_level()
        self.meshSettings['fineLevel'] = self.refinement
     
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
        create_boundary_conditions(self.meshSettings, self.boundaryConditions)    
        # go back to the main directory 
        os.chdir("..")
        # go inside the system directory
        os.chdir("system")
        # create the controlDict file
        ampersandIO.printMessage("Creating the system files")
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
        decomposeParDict = createDecomposeParDict(self.parallelSettings)
        ampersandPrimitives.write_dict_to_file("decomposeParDict", decomposeParDict)
        # go back to the main directory
        os.chdir("..")
        # create mesh script
        ampersandIO.printMessage("Creating the mesh and simulation scripts")
        meshScript = ScriptGenerator.generate_mesh_script(self.simulationFlowSettings)
        ampersandPrimitives.write_dict_to_file("mesh", meshScript)
        # create simulation script
        simulationScript = ScriptGenerator.generate_simulation_script(self.simulationFlowSettings)
        ampersandPrimitives.write_dict_to_file("run", simulationScript)
        ampersandPrimitives.crlf_to_LF("mesh")
        ampersandPrimitives.crlf_to_LF("run")


def main():
    project = ampersandProject()
    # Clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')
    ampersandIO.printMessage(get_ampersand_header())
    project.set_project_directory(ampersandPrimitives.ask_for_directory())
    project_name = ampersandIO.get_input("Enter the project name: ")
    project.set_project_name(project_name)
    #user_name = input("Enter the user name: ")
    #project.set_user_name(user_name)
    project.create_project_path()
    ampersandIO.printMessage("Creating the project")
    ampersandIO.printMessage(f"Project path: {project.project_path}")
    #project.project_path = r"C:\Users\Ridwa\Desktop\CFD\ampersandTests\drivAer2"
    project.create_project()
    project.create_settings()
    yN = ampersandIO.get_input("Add STL file to the project (y/N)?: ")
    while yN.lower() == 'y':
        project.add_stl_file()
        yN = ampersandIO.get_input("Add another STL file to the project (y/N)?: ")
    project.add_stl_to_project()
    # Before creating the project files, the settings are flushed to the project_settings.yaml file
    project.list_stl_files()
    project.ask_flow_type()
    if(project.internalFlow!=True):
        project.ask_ground_type()
    if(len(project.stl_files)>0):
        project.analyze_stl_file()

    #project.analyze_stl_file()
    project.write_settings()
    project.create_project_files()

if __name__ == '__main__':
    # Specify the output YAML file
    try:
        main()
    except KeyboardInterrupt:
        ampersandIO.printMessage("\nKeyboardInterrupt detected! Aborting project creation")
        exit()
    except Exception as error:
        ampersandIO.printError(error)
        exit()
