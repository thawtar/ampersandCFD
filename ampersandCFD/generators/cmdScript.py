"""
-------------------------------------------------------------------------------
  ***    *     *  ******   *******  ******    *****     ***    *     *  ******   
 *   *   **   **  *     *  *        *     *  *     *   *   *   **    *  *     *  
*     *  * * * *  *     *  *        *     *  *        *     *  * *   *  *     *  
*******  *  *  *  ******   ****     ******    *****   *******  *  *  *  *     *  
*     *  *     *  *        *        *   *          *  *     *  *   * *  *     *  
*     *  *     *  *        *        *    *   *     *  *     *  *    **  *     *  
*     *  *     *  *        *******  *     *   *****   *     *  *     *  ******   
-------------------------------------------------------------------------------
 * AmpersandCFD is a minimalist streamlined OpenFOAM generation tool.
 * Copyright (c) 2024 THAW TAR
 * All rights reserved.
 *
 * This software is licensed under the GNU General Public License version 3 (GPL-3.0).
 * You may obtain a copy of the license at https://www.gnu.org/licenses/gpl-3.0.en.html
 */
"""

import os
from pathlib import Path
from typing import Union
from ampersandCFD.models.settings import SimulationSettings
from ampersandCFD.utils.common import crlf_to_LF

class CmdScriptGenerator:
    @staticmethod
    def generate_mesh_script(settings: SimulationSettings):
        cmdMesh = f"""#!/bin/sh
cd "${{0%/*}}" || exit                                # Run from this directory
. ${{WM_PROJECT_DIR:?}}/bin/tools/RunFunctions        # Tutorial run functions
#-----------------------------------------------------
"""
        if (settings.parallel):
            cmdMesh += f"""
foamCleanTutorials
#cp -r 0 0.orig
rm -rf log.*
runApplication blockMesh
touch case.foam
runApplication surfaceFeatureExtract
runApplication decomposePar -force
runParallel snappyHexMesh -overwrite
runApplication reconstructParMesh -constant -latestTime
#rm -rf processor*
#rm log.decomposePar
#runApplication decomposePar -force
"""
        else:
            cmdMesh += f"""
runApplication blockMesh
touch case.foam
runApplication surfaceFeatureExtract
runApplication snappyHexMesh -overwrite
    """
        return cmdMesh

    # Generate run script for incompressible flow simulations (simpleFoam, pimpleFoam, etc.)
    @staticmethod
    def generate_run_script(settings: SimulationSettings):
        solver_name = settings.control.application
        cmdSimulation = f"""#!/bin/sh
cd "${{0%/*}}" || exit                                # Run from this directory
. ${{WM_PROJECT_DIR:?}}/bin/tools/RunFunctions        # Tutorial run functions
#-----------------------------------------------------
"""
        if (settings.parallel):
            cmdSimulation += f"""
#rm -rf 0
#cp -r 0.orig 0
rm -rf log.decomposePar log.simpleFoam log.pimpleFoam log.reconstructParMesh log.potentialFoam log.renumberMesh
runApplication decomposePar -force
touch case.foam
runParallel renumberMesh -overwrite
"""
            if (settings.control.potentialFoam):
                cmdSimulation += f"""
runParallel potentialFoam
runParallel {solver_name}
"""
            else:
                cmdSimulation += f"""
runParallel {solver_name}
"""

        else:
            if settings.control.potentialFoam:
                cmdSimulation += f"""
runApplication potentialFoam
runApplication {solver_name}
"""
            else:
                cmdSimulation += f"""
runApplication {solver_name}
"""
        return cmdSimulation

    # Generate postprocessing script
    @staticmethod
    def generate_postprocessing_script(settings: SimulationSettings):
        solver_name = settings.control.application

        cmdPostProcessing = f"""#!/bin/sh
cd "${{0%/*}}" || exit                                # Run from this directory
. ${{WM_PROJECT_DIR:?}}/bin/tools/RunFunctions        # Tutorial run functions
#-----------------------------------------------------
"""
        if (settings.parallel):
            cmdPostProcessing += f"""
runParallel {solver_name} -postProcess
"""
        else:
            cmdPostProcessing += f"""
runApplication {solver_name} -postProcess
"""
        return cmdPostProcessing

    @staticmethod
    def write(settings: SimulationSettings, project_path: Union[Path, str]):
        meshScript = CmdScriptGenerator.generate_mesh_script(settings)
        Path(f"{project_path}/mesh").write_text(meshScript)
        
        # create simulation script
        simulationScript = CmdScriptGenerator.generate_run_script(settings)
        Path(f"{project_path}/run").write_text(simulationScript)
        
        crlf_to_LF(f"{project_path}/mesh")
        crlf_to_LF(f"{project_path}/run")
        
        mesh_script = Path(project_path) / "mesh"
        run_script = Path(project_path) / "run"
        if os.name != 'nt':
            mesh_script.chmod(0o755)
            run_script.chmod(0o755)