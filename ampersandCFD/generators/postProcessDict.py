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

from pathlib import Path
from typing import Literal, Union
from ampersandCFD.utils.io import IOUtils
from ampersandCFD.models.settings import MeshSettings, PostProcessSettings, Location


class PostProcessGenerator:
    @staticmethod
    def generate_post_process_script():
        cmdPostProcess = f"""#!/bin/sh
cd "${{0%/*}}" || exit                                # Run from this directory
. ${{WM_PROJECT_DIR:?}}/bin/tools/RunFunctions        # Tutorial run functions
#-----------------------------------------------------
"""
        cmdPostProcess += f"""
runApplication postProcess
"""
        return cmdPostProcess

    @staticmethod
    # function object for showing minimum and maximum values of the fields
    def get_FO_min_max():
        FO = f"""
minMax
{{
    type        fieldMinMax;
    libs        ("fieldFunctionObjects");
    writeControl timeStep;
    ;
    fields
    (
        U
        p
    );
}}"""
        return FO

    @staticmethod
    def get_FO_yPlus():
        FO = f"""
yPlus1
{{
    // Mandatory entries
    type            yPlus;
    libs            (fieldFunctionObjects);
    writeControl    outputTime;
        writeInterval   1;
        writeFields     true;
    log             true;
}}
"""
        return FO

    @staticmethod
    def get_FO_forces(patchName="patchName", rhoInf=1, CofR=(0, 0, 0), pitchAxis=(0, 1, 0)):
        FO = f"""
forces
{{
    type            forces;
    libs            (forces);
    writeControl    timeStep;
    timeInterval    1;
    patches         ({patchName});
    rho             rhoInf;      // Indicates incompressible
    rhoInf          {rhoInf};           // Required when rho = rhoInf
    CofR            ({CofR[0]} {CofR[1]} {CofR[2]});  // Centre of rotation, used for moment calculation
    pitchAxis       ({pitchAxis[0]} {pitchAxis[1]} {pitchAxis[2]});  // Pitch axis
}}
"""
        return FO

    @staticmethod
    def FO_massFlow(patchName="patchName"):
        FO = f"""
{patchName}_massFlow
{{
    type            surfaceFieldValue;
    libs            ("libfieldFunctionObjects.so");
    writeControl    timeStep;
    timeInterval    1;
    log             true;
    writeFields     false;
    regionType      patch;
    name            {patchName};
    operation       sum;
    fields
    (
        phi
    );
}}
"""
        return FO

    @staticmethod
    def get_FO_probes(probeName="probeName", probeLocations:set[Location]=set([(0, 0, 0)])):
        FO = f"""
{probeName}
{{
    type            probes;
    libs            ("libfieldFunctionObjects.so");
    enabled         true;
    writeControl    timeStep;
    timeInterval    1;
    log				true;
    probeLocations
    (
"""
        for probeLocation in probeLocations:
            FO += f"        ({probeLocation[0]
                              } {probeLocation[1]} {probeLocation[2]})\n"
        FO += f"""    );
    fields
    (
        U
        p
    );
}}
"""
        return FO

    @staticmethod
    def FO_streamLines(start: Union[tuple, Literal["start"]] = "start", end: Union[tuple, Literal["end"]] = "end", nPoints=100):
        FO = f"""
streamLines
{{
    type            streamLines;
    libs            (streamLines);
    writeControl    timeStep;
    nPoints         {nPoints};
    start           ({start[0]} {start[1]} {start[2]});
    end             ({end[0]} {end[1]} {end[2]});
}}
"""
        return FO

    @staticmethod
    def get_probe_location():
        probeLocation = IOUtils.get_input_vector(
            "Enter probe location (x y z): ")
        return probeLocation

    @staticmethod
    def get_mass_flow_rate_FO(mesh_settings: MeshSettings):
        massFlowFO = ""
        # for internal flow problems, get all patches
        if (mesh_settings.internalFlow):
            for geometry_name, geometry in mesh_settings.geometry.items():
                patch_name = geometry_name.split(".")[0]
                if (geometry.type == "inlet" or geometry.type == "outlet"):
                    massFlowFO += PostProcessGenerator.FO_massFlow(patchName=patch_name)
                    # massFlowFO += postProcess.FO_massFlow(patchName=patch)
        else:
            # for external flow problems, there are only inlet and outlet patches
            massFlowFO += PostProcessGenerator.FO_massFlow(patchName="inlet")
            massFlowFO += PostProcessGenerator.FO_massFlow(patchName="outlet")
        return massFlowFO

    @staticmethod
    def generate_FOs(mesh_settings: MeshSettings, post_process_settings: PostProcessSettings, useFOs=True):
        if (not useFOs):
            return "// No function objects are used"
        FOs = ""
        if (post_process_settings.minMax):
            FOs += PostProcessGenerator.get_FO_min_max()
        if (post_process_settings.yPlus):
            FOs += PostProcessGenerator.get_FO_yPlus()
        if (post_process_settings.forces):
            FOs += PostProcessGenerator.get_FO_forces(patchName="wall",
                                         rhoInf=1, CofR=(0, 0, 0), pitchAxis=(0, 1, 0))
        if (post_process_settings.massFlow):
            FOs += PostProcessGenerator.get_mass_flow_rate_FO(mesh_settings)
        if (len(post_process_settings.probeLocations) > 0):
            FOs += PostProcessGenerator.get_FO_probes(probeName="probe",
                                         probeLocations=post_process_settings.probeLocations)
        # if(post_process_settings.streamLines):
        #    FOs += postProcess.FO_streamLines(start=(0,0,0),end=(0,0,1),nPoints=100)
        return FOs


    @staticmethod
    def write(mesh_settings: MeshSettings, post_process_settings: PostProcessSettings, project_path: Union[str, Path]):
        # Path(f"{project_path}/system/postProcessDict").write_text(PostProcess.generate_FOs(mesh_settings, post_process_settings))
        # Path(f"{project_path}/Allrun_postProcess").write_text(PostProcess.generate_post_process_script())
        Path(f"{project_path}/system/FOs").write_text(PostProcessGenerator.generate_FOs(mesh_settings, post_process_settings))