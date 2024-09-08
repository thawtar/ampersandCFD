import os
from primitives import ampersandPrimitives
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
# this file contains the functions to generate Case Directory for OpenFOAM
run_settings = {
    'mesh': True,
    'solver':'simpleFoam',
    'initialize':True,
    'postProc': True,
    'parallel': True
}

meshing_settings = {
    'blockMesh':True,
    'snappyHexMesh':True,
    'setFields':True,
    'topoSet':True
}

def ask_for_directory():
    root = Tk()
    root.withdraw()  # Hide the main window
    directory = filedialog.askdirectory(title="Select Project Directory")
    return directory if directory else None

def create_project_path_user(proj_path,project_name="testProject", user_name="user1"):
    
    if not proj_path:
        print("No directory selected. Aborting project creation.")
        return -1

    project_path = os.path.join(proj_path, user_name, project_name)
    print(project_path)
    return project_path

def create_project_path(proj_path,project_name="testProject"):
    #print(f"Creating Project: {project_name} ")
    
    # Ask for directory using the new function
    #default_path = ask_for_directory()
    
    if not proj_path:
        print("No directory selected. Aborting project creation.")
        return -1

    project_path = os.path.join(proj_path, project_name)
    print(project_path)
    return project_path


def create_project_directory(project_path):
    if os.path.exists(project_path):
        print("Directory exists")
    else:
        print("Creating project directory")
        try:
            os.makedirs(project_path)
            
        except OSError as error:
            print(error)
    try:
        os.chdir(project_path)
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

def write_settings():
    settings = {
        'meshSettings': meshSettings,
        'physicalProperties': physicalProperties,
        'numericalSettings': numericalSettings,
        'inletValues': inletValues,
        'boundaryConditions': boundaryConditions
    }
    ampersandPrimitives.dict_to_yaml(settings, 'project_settings.yaml')

def load_settings():
    settings = ampersandPrimitives.yaml_to_dict('project_settings.yaml')
    meshSettings = settings['meshSettings']
    physicalProperties = settings['physicalProperties']
    numericalSettings = settings['numericalSettings']
    inletValues = settings['inletValues']
    boundaryConditions = settings['boundaryConditions']
    caseSettings = (meshSettings, physicalProperties, numericalSettings, inletValues, boundaryConditions)
    return caseSettings


def create_project_files(caseSettings):
    (meshSettings, physicalProperties, numericalSettings, inletValues, boundaryConditions)=caseSettings
    
    # go inside the constant directory
    os.chdir("constant")
    # create transportProperties file
    tranP = create_transportPropertiesDict(physicalProperties)
    # create turbulenceProperties file
    turbP = create_turbulencePropertiesDict(physicalProperties)
    ampersandPrimitives.write_dict_to_file("transportProperties", tranP)
    ampersandPrimitives.write_dict_to_file("turbulenceProperties", turbP)
    # go back to the main directory
    os.chdir("..")
    # go inside the 0 directory
    os.chdir("0")
    # create the initial conditions file
    create_boundary_conditions(meshSettings, boundaryConditions, inletValues)    
    # go back to the main directory 
    os.chdir("..")
    # go inside the system directory
    os.chdir("system")
    # create the controlDict file
    controlDict = createControlDict(simulationSettings)
    ampersandPrimitives.write_dict_to_file("controlDict", controlDict)
    blockMeshDict = generate_blockMeshDict(meshSettings)
    ampersandPrimitives.write_dict_to_file("blockMeshDict", blockMeshDict)
    snappyHexMeshDict = generate_snappyHexMeshDict(meshSettings)
    ampersandPrimitives.write_dict_to_file("snappyHexMeshDict", snappyHexMeshDict)
    surfaceFeatureExtractDict = create_surfaceFeatureExtractDict(meshSettings)
    ampersandPrimitives.write_dict_to_file("surfaceFeatureExtractDict", surfaceFeatureExtractDict)
    
def main():
    project_path = ask_for_directory()
    if project_path is None:
        print("No directory selected. Aborting project creation.")
        return -1
    project_path = create_project_path(project_path)
    create_project_directory(project_path)
    write_settings()
    caseSettings=load_settings()
    #caseSettings=(meshSettings, physicalProperties, numericalSettings, inletValues, boundaryConditions)
    
    create_project_files(caseSettings)

def create_run(run_settings):
    cmdFlow = f"""
#!/bin/bash
cd "${{0%/*}}" || exit                                # Run from this directory
. ${{WM_PROJECT_DIR:?}}/bin/tools/RunFunctions        # Tutorial run functions
#------------------------------------------------------------------------------
foamCleanTutorials"""
    if(run_settings['parallel']):
        cmdFlow += f"""
runApplication decomposePar
runParallel renumberMesh -overwrite
"""
        if(run_settings['initialize']):
            cmdFlow += f"""runParallel potentialFoam"""
        cmdFlow += f"""runParallel {run_settings['solver']}"""
    else:
        if(run_settings['initialize']):
            cmdFlow += f"""runApplication potentialFoam"""
        cmdFlow += f"""runApplication {run_settings['solver']}"""
    return cmdFlow

if __name__ == '__main__':
    main()