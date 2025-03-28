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


from ampersandCFD.models.inputs import StlInput
from ampersandCFD.models.settings import BoundingBox, Domain, TriSurfaceMeshGeometry
from ampersandCFD.services.project_service import ProjectService
from ampersandCFD.utils.io import AmpersandDataInput, IOUtils, ModificationType
from ampersandCFD.models.project import AmpersandProject
from ampersandCFD.utils.stl_analysis import StlAnalysis


# A collection of functions that are used to modify the project
class ModService:
    @staticmethod
    def modify_project(project: AmpersandProject, modification_type: ModificationType):
        if modification_type == "Background Mesh":
            ModService.change_background_mesh(project)
        elif modification_type == "Mesh Point":
            ModService.change_mesh_point(project)
        elif modification_type == "Add Geometry":
            ModService.add_geometry(project)
        elif modification_type == "Refinement Levels":
            ModService.change_refinement_levels(project)
        elif modification_type == "Boundary Conditions":
            ModService.change_boundary_conditions(project)
        elif modification_type == "Fluid Properties":
            ModService.change_fluid_properties(project)
        raise ValueError("Invalid option. Aborting operation")


    @staticmethod
    # this is to change the global refinement level of the mesh
    def change_macro_refinement_level(project: AmpersandProject):
        IOUtils.print(f"Current refinement level: {project.settings.mesh.refAmount}")
        ref_amount_index = IOUtils.get_input_int("Enter new refinement level (0:coarse, 1:medium, 2:fine): ")
        if (ref_amount_index < 0 or ref_amount_index > 2):
            IOUtils.print("Invalid refinement level, please enter the value again")
            ModService.change_refinement_levels(project)

        ref_amounts = ["coarse", "medium", "fine"]
        project.settings.mesh.refAmount = ref_amounts[ref_amount_index] # type: ignore

    @staticmethod
    def change_domain_size(project: AmpersandProject, bounds: BoundingBox):
        project.settings.mesh.domain = Domain.update_size(project.settings.mesh.domain, bounds)
        IOUtils.print(f"Changed domain size (m)")
        IOUtils.print(project.settings.mesh.domain.__repr__())


    @staticmethod
    def change_mesh_size(project: AmpersandProject, cellSize: float):
        nx, ny, nz = StlAnalysis.calc_nx_ny_nz(project.settings.mesh.domain, cellSize)
        if (nx > 500 or ny > 500 or nz > 500):
            IOUtils.print("Warning: Mesh is too fine. Consider increasing the cell size")
        project.settings.mesh.domain = Domain.from_bbox(project.settings.mesh.domain, nx=nx, ny=ny, nz=nz)


    # this will allow the user to change the refinement level of the stl file
    @staticmethod
    def change_stl_refinement_level(project: AmpersandProject, stl_name: str):
        IOUtils.print("Changing refinement level")
        refMin = IOUtils.get_input_int("Enter new refMin: ")
        refMax = IOUtils.get_input_int("Enter new refMax: ")
        
        stl_geoemtry = project.settings.mesh.geometry[stl_name]
        assert isinstance(stl_geoemtry, TriSurfaceMeshGeometry), "Geometry is not a TriSurfaceMeshGeometry"
        stl_geoemtry.refineMin = refMin
        stl_geoemtry.refineMax = refMax
        stl_geoemtry.featureLevel = refMax


    # ---------------------------------------------------------------------#
    # The functions called when modifications are to be made project #

    @staticmethod
    def change_background_mesh(project: AmpersandProject):
        IOUtils.print("Current background mesh")
        IOUtils.print(project.settings.mesh.domain.__repr__())

        # ask whether to change domain size
        change_domain_size = IOUtils.get_input_bool("Change domain size (y/N)?: ")
        # ask new domain size
        if change_domain_size:
            bounds = AmpersandDataInput.get_domain_size()
            ModService.change_domain_size(project, bounds)
            IOUtils.print("Domain size changed")
        # ask new cell size
        change_mesh_size = IOUtils.get_input_bool("Change cell size (y/N)?: ")
        if change_mesh_size:
            cell_size = AmpersandDataInput.get_cell_size()
            project.settings.mesh.maxCellSize = cell_size
            # calculate new mesh size
            ModService.change_mesh_size(project, cell_size)
            IOUtils.print("Cell size changed")
        if change_domain_size or change_mesh_size:
            IOUtils.print(project.settings.mesh.domain.__repr__())
        else:
            IOUtils.print("No change in background mesh")

    @staticmethod 
    def add_geometry(project: AmpersandProject):
        IOUtils.print("Adding geometry")
        
        stl_inputs = AmpersandDataInput.get_valid_stl_inputs()
        last_stl_file = None
        for stl_input in stl_inputs:
            last_stl_file = ProjectService.add_stl_file(project, stl_input)
            
        project.summarize_stl_files()
        return last_stl_file

    @staticmethod
    def change_refinement_levels(project: AmpersandProject):
        IOUtils.print("Changing refinement levels")
        stl_file_name = ModService.choose_stl_file(project)
        ModService.change_stl_refinement_level(project, stl_file_name)


    @staticmethod
    def choose_stl_file(project: AmpersandProject) -> str:
        stl_file_names = project.summarize_stl_files()
        stl_file_number = IOUtils.get_input("Enter the number of the file: ")
        try:
            stl_file_number = int(stl_file_number)
            if stl_file_number <= 0 or stl_file_number > len(stl_file_names):
                raise ValueError("Invalid input. Please try again.")

            project.summarize_stl_files()
            return stl_file_names[stl_file_number-1]

        except ValueError:
            IOUtils.print("Invalid input. Please try again.")
            return ModService.choose_stl_file(project)


    @staticmethod
    def change_mesh_point(project: AmpersandProject):
        IOUtils.print("Changing mesh points")
        currentMeshPoint = project.settings.mesh.castellatedMeshControls.locationInMesh
        IOUtils.print(f"Current mesh points: ({currentMeshPoint[0]},{currentMeshPoint[1]},{currentMeshPoint[2]})")

        x, y, z = IOUtils.get_input_vector("Enter new mesh points: ")
        project.settings.mesh.castellatedMeshControls.locationInMesh = (x, y, z)
        IOUtils.print(
            f"New mesh points: ({currentMeshPoint[0]},{currentMeshPoint[1]},{currentMeshPoint[2]})")

    @staticmethod
    def change_boundary_conditions(project: AmpersandProject):
        IOUtils.print("Changing boundary conditions")
        boundary_conditions = project.summarize_boundary_conditions()

        bc_number = IOUtils.get_input( "Enter the number of the boundary to change: ")
        try:
            bc_number = int(bc_number)
            if bc_number <= 0 or bc_number > len(boundary_conditions):
                IOUtils.print("Invalid input. Please try again.")
            else:
                bc = boundary_conditions[bc_number-1]
                IOUtils.print(f"Changing boundary condition for patch: {bc}")
                patch_type = AmpersandDataInput.get_patch_type()
                patch_property = AmpersandDataInput.get_patch_property()

                project.update_patch(bc, patch_type, patch_property)
        except ValueError:
            IOUtils.print("Invalid input. Please try again.")
            ModService.change_boundary_conditions(project)

    @staticmethod
    def change_fluid_properties(project: AmpersandProject):
        IOUtils.print("Current fluid properties")
        IOUtils.print(f"Density: {project.settings.physicalProperties.rho}")
        IOUtils.print(f"Kinematic viscosity: {project.settings.physicalProperties.nu}")
        fluid = AmpersandDataInput.choose_fluid_properties()
        project.settings.physicalProperties.fluid = fluid


