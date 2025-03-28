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
from ampersandCFD.models.settings import MeshSettings, TriSurfaceMeshGeometry
from ampersandCFD.utils.generation import GenerationUtils

SurfaceExtractObjectType = Literal["surfaceFeatureExtractDict", "surfaceFeaturesDict"]

class SurfaceExtractorDictGenerator:
    @staticmethod
    def generate(mesh_settings: MeshSettings, type: SurfaceExtractObjectType) -> str:
        surfaceDict = GenerationUtils.createFoamHeader("dictionary", type)
        for geometry_name, geometry in mesh_settings.geometry.items():
            if isinstance(geometry, TriSurfaceMeshGeometry):
                surfaceDict += f"""\n{geometry_name}
    {{
    extractionMethod    extractFromSurface;
    includedAngle   170;
    subsetFeatures
    {{
        nonManifoldEdges       no;
        openEdges       yes;
    }}
    writeObj            yes;
    writeSets           no;
    }}"""
        return surfaceDict


    @staticmethod
    def write(mesh_settings: MeshSettings, type: SurfaceExtractObjectType, project_path: Union[str, Path]):
        Path(f"{project_path}/system/{type}").write_text(SurfaceExtractorDictGenerator.generate(mesh_settings, type))
