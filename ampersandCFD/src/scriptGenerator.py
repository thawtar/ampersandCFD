import os
import sys

class ScriptGenerator:
    def __init__(self):
        pass

    @staticmethod
    def generate_mesh_script(simulationFlowSettings):
        cmdMesh = f"""
    #!/bin/bash
    cd "${{0%/*}}" || exit                                # Run from this directory
    . ${{WM_PROJECT_DIR:?}}/bin/tools/RunFunctions        # Tutorial run functions
    #-----------------------------------------------------
    """
        if(simulationFlowSettings['parallel']):
            cmdMesh += f"""
    runApplication blockMesh
    runApplication surfaceFeatureExtract
    runApplication decomposePar -force
    runParallel snappyHexMesh -overwrite
    runApplication reconstructParMesh -constant -latestTime
    """
        else:
            cmdMesh += f"""
    runApplication blockMesh
    runApplication surfaceFeatureExtract
    runApplication snappyHexMesh -overwrite
    """
        return cmdMesh

    # Generate run script for incompressible flow simulations (simpleFoam, pimpleFoam, etc.)
    @staticmethod
    def generate_simulation_script(simulationFlowSettings):
        cmdSimulation = f"""
    #!/bin/bash
    cd "${{0%/*}}" || exit                                # Run from this directory
    . ${{WM_PROJECT_DIR:?}}/bin/tools/RunFunctions        # Tutorial run functions
    #-----------------------------------------------------
    """
        if(simulationFlowSettings['parallel']):
            cmdSimulation += f"""
    cp -r 0.orig 0
    runApplication decomposePar -force
    runParallel renumberMesh -overwrite
    """
            if(simulationFlowSettings['potentialFoam']):
                cmdSimulation += f"""
    runParallel potentialFoam
    runParallel {simulationFlowSettings['solver']}
    """
            else:
                cmdSimulation += f"""
    runParallel {simulationFlowSettings['solver']}
    """
            
        else:
            if simulationFlowSettings['potentialFoam']:
                cmdSimulation += f"""
    runApplication potentialFoam
    runApplication {simulationFlowSettings['solver']}
    """
            else:
                cmdSimulation += f"""   
    runApplication {simulationFlowSettings['solver']}
    """
        return cmdSimulation

    # Generate postprocessing script
    @staticmethod
    def generate_postprocessing_script(simulationFlowSettings):
        cmdPostProcessing = f"""
    #!/bin/bash
    cd "${{0%/*}}" || exit                                # Run from this directory
    . ${{WM_PROJECT_DIR:?}}/bin/tools/RunFunctions        # Tutorial run functions
    #-----------------------------------------------------
    """
        if(simulationFlowSettings['parallel']):
            cmdPostProcessing += f"""
    runParallel {simulationFlowSettings['solver']} -postProcess
    """
        else:
            cmdPostProcessing += f"""
    runApplication {simulationFlowSettings['solver']} -postProcess
    """
        return cmdPostProcessing
    
    