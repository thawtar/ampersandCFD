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
from ampersandCFD.models.settings import ControlSettings
from ampersandCFD.utils.io import IOUtils
from ampersandCFD.utils.generation import GenerationUtils


class ControlDictGenerator:
    @staticmethod
    def generate(control_settings: ControlSettings):
        return f"""{GenerationUtils.createFoamHeader('dictionary', 'controlDict')}
application     {control_settings.application};
startFrom       {control_settings.startFrom};
startTime       {control_settings.startTime};
stopAt          {control_settings.stopAt};
endTime         {control_settings.endTime};
deltaT          {control_settings.deltaT};
writeControl    {control_settings.writeControl};
writeInterval   {control_settings.writeInterval};
purgeWrite      {control_settings.purgeWrite};
writeFormat     {control_settings.writeFormat};
writePrecision  {control_settings.writePrecision};
writeCompression {control_settings.writeCompression};
timeFormat      {control_settings.timeFormat};
timePrecision   {control_settings.timePrecision};
runTimeModifiable {control_settings.runTimeModifiable};
adjustTimeStep  {control_settings.adjustTimeStep};
maxCo           {control_settings.maxCo};
functions
{{
    #include "FOs"
}};
libs
(
);
"""

    @staticmethod
    def write(control_settings: ControlSettings, project_path: Union[str, Path]):
        Path(f"{project_path}/system/controlDict").write_text(ControlDictGenerator.generate(control_settings))
