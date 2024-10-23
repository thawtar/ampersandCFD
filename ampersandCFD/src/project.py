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
from constants import simulationFlowSettings, parallelSettings, postProcessSettings
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
from postProcess import postProcess
from mod_project import mod_project


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
        self.postProcessSettings = None
        self.settings = None
        self.project_path = None
        self.existing_project = False # flag to check if the project is already existing
        self.stl_files = [] # list to store the settings for stl files
        self.stl_names = [] # list to store the names of the stl files
        self.internalFlow = False # default is external flow
        self.onGround = False # default is off the ground
        self.halfModel = False # default is full model
        self.parallel = True # default is parallel simulation
        self.snap = True # default is to use snappyHexMesh
        self.transient = False # default is steady state
        self.refinement = 0 # 0: coarse, 1: medium, 2: fine
        self.characteristicLength = None # default characteristic length
        self.useFOs = False # default is not to use function objects
        self.current_modification = None # current modification to the project settings
        self.mod_options = ["Background Mesh","Add Geometry","Refinement Levels","Boundary Conditions","Fluid Properties", "Numerical Settings", 
                   "Simulation Control Settings","Turbulence Model","Post Processing Settings"]

    def summarize_project(self):
        trueFalse = {True: 'Yes', False: 'No'}
        ampersandIO.show_title("Project Summary")
        #ampersandIO.printMessage(f"Project directory: {self.project_directory_path}")
        ampersandIO.printFormat("Project name", self.project_name)
        ampersandIO.printFormat("Project path", self.project_path)
        #ampersandIO.printMessage(f"Project path: {self.project_path}")
       
        #ampersandIO.printMessage(f"Existing project: {self.existing_project}")
        #ampersandIO.printMessage(f"STL files: {self.stl_names}")
        ampersandIO.printMessage(f"Internal Flow: {trueFalse[self.internalFlow]}")
        if(self.internalFlow==False):
            ampersandIO.printMessage(f"On Ground: {trueFalse[self.onGround]}")
        ampersandIO.printMessage(f"Transient: {trueFalse[self.transient]}")
        
        #ampersandIO.printMessage("Boundary Conditions")
        #ampersandIO.print_dict(self.boundaryConditions)
    
    def choose_modification(self):
        current_modification = ampersandIO.get_option_choice(prompt="Choose any option for project modification: ",
                                      options=self.mod_options,title="\nModify Project Settings")
        self.current_modification = self.mod_options[current_modification]
        ampersandIO.printMessage(f"Current modification: {self.current_modification}")
        


    def modify_project(self):
        if self.current_modification=="Background Mesh":
            mod_project.change_background_mesh(self)
        elif self.current_modification=="Add Geometry":
            mod_project.add_geometry(self)
        elif self.current_modification=="Refinement Levels":
            mod_project.change_refinement_levels(self)
        elif self.current_modification=="Boundary Conditions":
            mod_project.change_boundary_conditions(self)
        elif self.current_modification=="Fluid Properties":
            mod_project.change_fluid_properties(self)
        elif self.current_modification=="Numerical Settings":
            mod_project.change_numerical_settings(self)
        elif self.current_modification=="Simulation Control Settings":
            mod_project.change_simulation_settings(self)
        elif self.current_modification=="Turbulence Model":
            mod_project.change_turbulenc_model(self)
        elif self.current_modification=="Post Processing Settings":
            mod_project.change_post_process_settings(self)
        else:
            ampersandIO.printMessage("Invalid option. Aborting operation")
            return -1
        return 0
    
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
        
    # To create the project path for a new project with the project name
    def create_project_path(self):
        if not self.project_directory_path:
            ampersandIO.printMessage("No directory selected. Aborting project creation.")
            return -1
        self.project_path = os.path.join(self.project_directory_path, self.project_name)
    
    # this is to set the project path if the project is already existing
    # useful for opening existing projects and modifying the settings
    def set_project_path(self,project_path):
        if project_path is None:
            ampersandIO.printMessage("No project path selected. Aborting project creation.")
            exit()
        if os.path.exists(project_path):
            settings_file = os.path.join(project_path, "project_settings.yaml")
            if os.path.exists(settings_file):
                ampersandIO.printMessage("Project found, loading project settings")
                self.existing_project = True
                self.project_path = project_path
                return 0
            else:
                ampersandIO.printMessage("Settings file not found. Creating a new project here.")
                # TO DO: Add the code socket to create a new project here
                return -1
        else:
            ampersandIO.printMessage("Project path does not exist. Aborting project creation/opening.")
            return -1

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
        
    # Wrapper of cwd with error handling
    def go_inside_directory(self):
        try:
            os.chdir(self.project_path)
        except OSError as error:
                ampersandIO.printError(error)
        cwd = os.getcwd()
        ampersandIO.printMessage(f"Working directory: {cwd}")

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
            'postProcessSettings': self.postProcessSettings
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
        self.postProcessSettings = settings['postProcessSettings']
        for geometry in self.meshSettings['geometry']:
            if(geometry['type']=='triSurfaceMesh'):
                if(geometry['name'] in self.stl_names):
                    ampersandIO.printMessage(f"STL file {geometry['name']} already exists in the project, skipping the addition")
                else:
                    self.stl_files.append(geometry)
                    self.stl_names.append(geometry['name'])
        # Change project settings based on loaded settings
        self.internalFlow = self.meshSettings['internalFlow']
        self.onGround = self.meshSettings['onGround']
        self.transient = self.simulationSettings['transient']
        #self.parallel = self.parallelSettings['parallel']
        #self.snap = self.meshSettings['snap']
        self.refinement = self.meshSettings['fineLevel']
        #self.characteristicLength = self.meshSettings['characteristicLength']
        self.useFOs = self.postProcessSettings['FOs']
        project_name = self.project_path.split("/")[-1]
        self.project_name = project_name

        
    def show_settings(self):
        ampersandIO.printMessage("Project settings")
        ampersandIO.printMessage("Mesh Settings")
        ampersandIO.print_dict(self.meshSettings)
        ampersandIO.printMessage("Physical Properties")
        ampersandIO.print_dict(self.physicalProperties)
        ampersandIO.printMessage("Numerical Settings")
        ampersandIO.print_dict(self.numericalSettings)
        ampersandIO.printMessage("Inlet Values")
        ampersandIO.print_dict(self.inletValues)
        ampersandIO.printMessage("Boundary Conditions")
        ampersandIO.print_dict(self.boundaryConditions)
        ampersandIO.printMessage("Solver Settings")
        ampersandIO.print_dict(self.solverSettings)
        ampersandIO.printMessage("Simulation Settings")
        ampersandIO.print_dict(self.simulationSettings)
        ampersandIO.printMessage("Parallel Settings")
        ampersandIO.print_dict(self.parallelSettings)
        ampersandIO.printMessage("Simulation Flow Settings")
        ampersandIO.print_dict(self.simulationFlowSettings)
        ampersandIO.printMessage("Post Process Settings")
        ampersandIO.print_dict(self.postProcessSettings)

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
        self.postProcessSettings = postProcessSettings
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
    def add_stl_to_mesh_settings(self, stl_name,refMin=0, refMax=0, featureEdges='true', 
                                 featureLevel=1,purpose='wall',property=None,bounds=None):
        already_exists = False # flag to check if the stl file already exists in the project
        idx = 0 # index of the stl file in the list
        # Purpose is wall by default
        # Other purposes are patch, refinementRegion, refinementSurface, cellZone, baffles
        if self.refinement == 0:
            nLayers = 3
        elif self.refinement == 1:
            nLayers = 5
        else:
            nLayers = 7
        stl_ = {'name': stl_name, 'type':'triSurfaceMesh','purpose':purpose, 'refineMin': refMin, 'refineMax': refMax, 
                'featureEdges':featureEdges, 'featureLevel':featureLevel, 'nLayers':nLayers, 'property':property, 'bounds':bounds}
        
        # this snippet is to prevent the same stl file from being added multiple times
        # Instead of using set, we are using a list to store the stl files
        # To check if the stl file already exists in the project, stl names are compared.
        # list all the stl files in the project
        for stl_name in self.stl_names:
            if stl_name == stl_['name']:
                ampersandIO.printMessage(f"STL file {stl_name} already exists in the project")
                already_exists = True
                break
            idx += 1
        if not already_exists:
            self.stl_names.append(stl_name)
            self.stl_files.append(stl_)
        else:    
            self.stl_files[idx] = stl_
            return 1 # flag to indicate that the stl file is replaced
        return 0

    

    def ask_purpose(self):
        purposes = ['wall', 'inlet','outlet', 'refinementRegion', 'refinementSurface', 'cellZone', 'baffles']
        ampersandIO.printMessage(f"Enter purpose for this STL geometry")
        ampersandIO.print_numbered_list(purposes)
        purpose_no = ampersandIO.get_input_int("Enter purpose number: ")-1
        if(purpose_no < 0 or purpose_no > len(purposes)-1):
                ampersandIO.printMessage("Invalid purpose number. Setting purpose to wall")
                purpose = 'wall'
        else:
            purpose = purposes[purpose_no]
        return purpose
    
    def set_property(self,purpose='wall'):
        if purpose == 'inlet':
            U = ampersandDataInput.get_inlet_values()
            property = tuple(U)
            ampersandIO.printMessage(f"Setting property of {purpose} to {property}")
        elif purpose == 'refinementRegion' or purpose == 'cellZone':
            refLevel = ampersandIO.get_input_int("Enter refinement level: ")
            property = refLevel
        elif purpose == 'refinementSurface':
            refLevel = ampersandIO.get_input_int("Enter refinement level: ")
            property = refLevel
        else:
            property = None
        return property
    
   
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
                
                purpose = self.ask_purpose()
                bounds = stlAnalysis.compute_bounding_box(stl_file)
                bounds = tuple(bounds)
                property = self.set_property(purpose)
                self.add_stl_to_mesh_settings(stl_name,purpose=purpose,property=property,bounds=bounds)
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
            
    # this is a wrapper of the primitives 
    def list_stl_files(self):
        ampersandPrimitives.list_stl_files(self.stl_files)


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
        self.meshSettings['internalFlow'] = self.internalFlow

    def ask_transient(self):
        transient = ampersandIO.get_input("Transient or Steady State (T/S)?: ")
        if transient.lower() == 't':
            self.transient = True
        else:
            self.transient = False

    def ask_half_model(self):
        half_model = ampersandIO.get_input_bool("Half Model (y/N)?: ")
        if half_model==True:
            self.halfModel = True
            self.meshSettings['halfModel'] = True
            # if the model is half, the back patch should be symmetry
            ampersandPrimitives.change_patch_type(self.meshSettings['patches'],patch_name='back'
                                                  ,new_type='symmetry')
        else:
            self.halfModel = False
            self.meshSettings['halfModel'] = False


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
                                                                           refinement=self.refinement,halfModel=self.halfModel)
        featureLevel = max(refLevel,1)
        self.meshSettings = stlAnalysis.set_mesh_settings(self.meshSettings, domain_size, nx, ny, nz, refLevel, featureLevel) 
        self.meshSettings = stlAnalysis.set_mesh_location(self.meshSettings, stl_path,self.internalFlow)
        refinementBoxLevel = max(2,refLevel-3)
        self.meshSettings = stlAnalysis.addRefinementBoxToMesh(meshSettings=self.meshSettings, stl_path=stl_path,refLevel=refinementBoxLevel,internalFlow=self.internalFlow)
        if(self.internalFlow==False and self.onGround==True):
            # if the flow is external and the geometry is on the ground, add a ground refinement box
            self.meshSettings = stlAnalysis.addGroundRefinementBoxToMesh(meshSettings=self.meshSettings, stl_path=stl_path,refLevel=refinementBoxLevel)
        #self.meshSettings = stlAnalysis.set_layer_thickness(self.meshSettings, target_y)
        self.meshSettings = stlAnalysis.set_min_vol(self.meshSettings, minVol)
        return 0
    
    def set_inlet_values(self):
        if(not self.internalFlow): # external flow
            U = ampersandDataInput.get_inlet_values()
            self.inletValues['U'] = U
            self.boundaryConditions['velocityInlet']['u_value'] = U
        else: # internal flow
            # Use inlet values from the stl file
            ampersandIO.printMessage("Setting inlet values for various inlet boundaries")
            for stl_file in self.stl_files:
                if stl_file['purpose'] == 'inlet':
                    U = list(stl_file['property'])
                    self.boundaryConditions['velocityInlet']['u_value'] = U
                    self.inletValues['U'] = U
        

    def set_fluid_properties(self):
        fluid = ampersandDataInput.choose_fluid_properties()
        if fluid == -1:
            rho, nu = ampersandDataInput.get_physical_properties()
            fluid = {'rho':rho, 'nu':nu}
        self.physicalProperties['rho'] = fluid['rho']
        self.physicalProperties['nu'] = fluid['nu']

    #def set_transient(self):
    #    self.transient = ampersandIO.get_input_bool("Transient simulation (y/N)?: ")

    def set_parallel(self):
        n_core = ampersandIO.get_input_int("Number of cores for parallel simulation: ")
        self.parallelSettings['numberOfSubdomains'] = n_core
    
    
    def set_transient_settings(self):
        self.ask_transient()
        if self.transient:
            ampersandIO.printMessage("Transient simulation settings")
            self.simulationSettings['solver'] = 'pimpleFoam'
            self.simulationFlowSettings['solver'] = 'pimpleFoam'
            self.simulationSettings['endTime'] = ampersandIO.get_input_float("End time: ")
            self.simulationSettings['writeInterval'] = ampersandIO.get_input_float("Write interval: ")
            self.simulationSettings['deltaT'] = ampersandIO.get_input_float("Time step: ")
            self.simulationSettings['adjustTimeStep'] = 'no'
            self.simulationSettings['maxCo'] = 0.9
            self.numericalSettings['ddtSchemes'] = 'Euler'
            # if steady state, SIMPLEC is used. If transient, PIMPLE is used
            # for PIMPLE, the relaxation factors are set to 0.7 and p = 0.3
            self.numericalSettings['relaxationFactors']['p'] = 0.3
            

    def ask_ground_type(self):
        ground_type = ampersandIO.get_input_bool("Is the ground touching the body (y/N): ")
        if ground_type:
            self.onGround = True
            self.meshSettings['onGround'] = True
            ampersandPrimitives.change_patch_type(self.meshSettings['patches'],patch_name='ground',
                                                    new_type='wall')
        else:
            self.onGround = False
            self.meshSettings['onGround'] = False

    def ask_refinement_level(self):
        self.refinement = ampersandDataInput.get_mesh_refinement_level()
        self.meshSettings['fineLevel'] = self.refinement

    def set_post_process_settings(self):
        if self.useFOs:
            self.postProcessSettings['FOs'] = True
        meshPoint = list(self.meshSettings['castellatedMeshControls']['locationInMesh'])
        self.postProcessSettings['massFlow'] = True
        self.postProcessSettings['minMax'] = True
        self.postProcessSettings['yPlus'] = True
        self.postProcessSettings['forces'] = True
        # the default probe location for monitoring of flow variables
        self.postProcessSettings['probeLocations'].append(meshPoint)

    def get_probe_location(self):
        point = postProcess.get_probe_location()
        # for internal flows, the point should be inside stl
        # for external flows, the point should be outside stl
        # TO DO
        self.postProcessSettings['probeLocations'].append(point)
     
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
        FODict = postProcess.create_FOs(self.meshSettings,self.postProcessSettings,useFOs=self.useFOs)
        ampersandPrimitives.write_dict_to_file("FOs", FODict)
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
