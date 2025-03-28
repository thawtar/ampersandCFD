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
from ampersandCFD.models.settings import PhysicalProperties
from ampersandCFD.utils.generation import GenerationUtils

class ConstantDictGenerator:
    @staticmethod
    def generate_transport_dict(physical_properties: PhysicalProperties):
        header = GenerationUtils.createFoamHeader(className="dictionary",
                                                objectName="transportProperties")
        transportPropertiesDict = f""+header
        transportProperties_ = f"""
    transportModel  Newtonian;
    nu              nu [ 0 2 -1 0 0 0 0 ] {physical_properties.nu};
    """
        transportPropertiesDict += transportProperties_
        return transportPropertiesDict


    @staticmethod
    def generate_turbulence_dict(physical_properties: PhysicalProperties):
        header = GenerationUtils.createFoamHeader(className="dictionary",
                                                objectName="turbulenceProperties")
        turbulencePropertiesDict = f""+header
        turbulenceProperties_ = f"""
    simulationType  RAS;
    RAS
    {{
        RASModel        {physical_properties.turbulenceModel};
        turbulence      on;
        printCoeffs     on;
        Cmu             0.09;
    }}
    """
        turbulencePropertiesDict += turbulenceProperties_
        return turbulencePropertiesDict



    @staticmethod
    def write(physical_properties: PhysicalProperties, project_path: Union[str, Path]):
        Path(f"{project_path}/constant/transportProperties").write_text(ConstantDictGenerator.generate_transport_dict(physical_properties))
        Path(f"{project_path}/constant/turbulenceProperties").write_text(ConstantDictGenerator.generate_turbulence_dict(physical_properties))
