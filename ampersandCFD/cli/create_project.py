# %%
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
from ampersandCFD.models.inputs import CreateProjectInput, TransientInput
from ampersandCFD.utils.io import AmpersandDataInput, IOUtils
from ampersandCFD.services.project_service import ProjectService


def create_project():
    
    parent_directory = IOUtils.ask_for_directory()
    project_name = IOUtils.get_input("Enter the project name: ")
    project_path = Path(f"{parent_directory}/{project_name}")

    IOUtils.print(f"Project path: {project_path}")

    IOUtils.print("Preparing for mesh generation")
    refinement_amount = AmpersandDataInput.get_mesh_refinement_amount()
    add_stls = IOUtils.get_input("Add STL file to the project (y/N)?: ").lower() == 'y'
    stl_files = AmpersandDataInput.get_valid_stl_inputs() if add_stls else []

    is_internal_flow = IOUtils.get_input("Internal or External Flow (I/E)?: ").lower() == 'i'

    on_ground_type = False
    inlet_values = None
    if (not is_internal_flow):
        on_ground_type = IOUtils.get_input_bool("Is the ground touching the body (y/N): ")
        inlet_values = AmpersandDataInput.get_inlet_values()

    IOUtils.print( "Fluid properties and inlet values are necessary for mesh size calculations")

    fluid = AmpersandDataInput.choose_fluid_properties()
    is_transient = IOUtils.get_input("Transient or Steady State (T/S)?: ").lower() == 't'

    if (is_transient):
        end_time = IOUtils.get_input_int("End time: ")
        write_interval = IOUtils.get_input_int("Write interval: ")
        time_step = IOUtils.get_input_int("Time step: ")
        transient = TransientInput(
            end_time=end_time,
            time_step=time_step,
            write_interval=write_interval,
        )
    else:
        transient = False

    n_core = IOUtils.get_input_int("Number of cores for parallel simulation: ")
    half_model = IOUtils.get_input_bool("Half Model (y/N)?: ")
    useFOs = IOUtils.get_input_bool("Use function objects for post-processing (y/N)?: ")


    input = CreateProjectInput(
        refinement_amount=refinement_amount,
        is_internal_flow=is_internal_flow,
        on_ground=on_ground_type,
        fluid=fluid,
        inlet_values=inlet_values,
        transient=transient,
        n_core=n_core,
        is_half_model=half_model,
        use_function_objects=useFOs,
        stl_files=stl_files
    )



    project = ProjectService.create_project(project_path, input)
    project.summarize_project()
