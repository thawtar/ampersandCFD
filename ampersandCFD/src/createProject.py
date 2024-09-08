


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