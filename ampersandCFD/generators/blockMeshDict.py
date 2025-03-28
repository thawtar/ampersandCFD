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
from typing import Union
from ampersandCFD.models.settings import MeshSettings
from ampersandCFD.utils.generation import GenerationUtils


class BlockMeshDictGenerator:
    @staticmethod
    def generate(mesh_settings: MeshSettings) -> str:
        return f"""{GenerationUtils.createFoamHeader("dictionary", "blockMeshDict")}

// ********* Domain *********
scale {mesh_settings.scale};

vertices
(
    ({mesh_settings.domain.minx} {mesh_settings.domain.miny} {mesh_settings.domain.minz})
    ({mesh_settings.domain.maxx} {mesh_settings.domain.miny} {mesh_settings.domain.minz})
    ({mesh_settings.domain.maxx} {mesh_settings.domain.maxy} {mesh_settings.domain.minz})
    ({mesh_settings.domain.minx} {mesh_settings.domain.maxy} {mesh_settings.domain.minz})
    ({mesh_settings.domain.minx} {mesh_settings.domain.miny} {mesh_settings.domain.maxz})
    ({mesh_settings.domain.maxx} {mesh_settings.domain.miny} {mesh_settings.domain.maxz})
    ({mesh_settings.domain.maxx} {mesh_settings.domain.maxy} {mesh_settings.domain.maxz})
    ({mesh_settings.domain.minx} {mesh_settings.domain.maxy} {mesh_settings.domain.maxz})
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({mesh_settings.domain.nx} {mesh_settings.domain.ny} {mesh_settings.domain.nz}) simpleGrading (1 1 1)
);

edges
(
);

boundary
({"\n".join(
        f"""
    {patch_name}
    {{
        type {patch.bcType};
        faces
        (
            ({patch.faces[0]} {patch.faces[1]} {patch.faces[2]} {patch.faces[3]})
        );
    }}
""" for patch_name, patch in mesh_settings.patches.items())}

);
mergePatchPairs
(
);

// ************************************************************************* //
"""
    @staticmethod
    def write(mesh_settings: MeshSettings, project_path: Union[str, Path]):
        Path(f"{project_path}/system/blockMeshDict").write_text(BlockMeshDictGenerator.generate(mesh_settings))
