import os
from primitives import ampersandPrimitives
from constants import meshSettings, physicalProperties, numericalSettings, inletValues
from constants import boundaryConditions
from blockMeshGenerator import generate_blockMeshDict
from snappyHexMeshGenerator import generate_snappyHexMeshDict
from surfaceExtractor import create_surfaceFeatureExtractDict
from transportAndTurbulence import create_transportPropertiesDict, create_turbulencePropertiesDict
from boundaryConditionsGenerator import create_boundary_conditions

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

def write_settings():
    # write meshSettings to file
    ampersandPrimitives.dict_to_yaml(meshSettings, 'meshSettings.yaml')
    # write physicalProperties to file
    ampersandPrimitives.dict_to_yaml(physicalProperties, 'physicalProperties.yaml')
    # write numericalSettings to file
    ampersandPrimitives.dict_to_yaml(numericalSettings, 'numericalSettings.yaml')
    # write inletValues to file
    ampersandPrimitives.dict_to_yaml(inletValues, 'inletValues.yaml')
    # write boundaryConditions to file
    ampersandPrimitives.dict_to_yaml(boundaryConditions, 'boundaryConditions.yaml')

def load_settings():
    meshSettings = ampersandPrimitives.yaml_to_dict('meshSettings.yaml')
    physicalProperties = ampersandPrimitives.yaml_to_dict('physicalProperties.yaml')
    numericalSettings = ampersandPrimitives.yaml_to_dict('numericalSettings.yaml')
    inletValues = ampersandPrimitives.yaml_to_dict('inletValues.yaml')
    boundaryConditions = ampersandPrimitives.yaml_to_dict('boundaryConditions.yaml')
    caseSettings = (meshSettings, physicalProperties, numericalSettings, inletValues, boundaryConditions)
    return caseSettings

def create_project(project_name="testProject",user_name="user1"):
    print(f"Creating Project: {project_name} for {user_name}")
    # create directory at the /$HOME/user_name/project_name
    default_path = r"C:\Users\Ridwa\Desktop\CFD\ampersandTests"
    project_path = os.path.join(default_path,user_name,project_name)
    print(project_path)
    # check whether the path already exists. If not, create the path
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



def create_project_files(caseSettings):
    (meshSettings, physicalProperties, numericalSettings, inletValues, boundaryConditions)=caseSettings

    # go inside the constant directory
    os.chdir("constant")
    # create transportProperties file
    create_transportPropertiesDict(physicalProperties)
    # create turbulenceProperties file
    create_turbulencePropertiesDict(physicalProperties)
    # go back to the main directory
    os.chdir("..")
    # go inside the 0 directory
    os.chdir("0")
    # create the initial conditions file
    create_boundary_conditions(meshSettings, boundaryConditions, inletValues)    


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
    create_project("sloshing","user1")
    print(create_run(run_settings))