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
from ampersandCFD.models.settings import ParallelSettings
from ampersandCFD.utils.generation import GenerationUtils

class DecomposeParDictGenerator:
    @staticmethod
    def generate(parallel_settings: ParallelSettings) -> str:
        decomposeParDict = f"""{GenerationUtils.createFoamHeader('dictionary', 'decomposeParDict')}
numberOfSubdomains {parallel_settings.numberOfSubdomains};
method {parallel_settings.method};
"""
        return decomposeParDict

    @staticmethod
    def write(parallel_settings: ParallelSettings, project_path: Union[str, Path]):
        Path(f"{project_path}/system/decomposeParDict").write_text(DecomposeParDictGenerator.generate(parallel_settings))
