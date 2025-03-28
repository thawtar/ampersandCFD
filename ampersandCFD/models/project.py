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
from typing import Optional, Union
from ampersandCFD.models.settings import SimulationSettings, TriSurfaceMeshGeometry, PatchType, PatchProperty
from ampersandCFD.utils.io import IOUtils


class AmpersandProject: 
    def __init__(self, project_path: Union[str, Path], settings: Optional[SimulationSettings] = None):
        self.settings = settings or SimulationSettings()
        self.project_path = Path(project_path)
    
    @property
    def name(self):
        return self.project_path.name

    def update_patch(self, name: str, type: PatchType, property: Optional[PatchProperty] = None):
        if not self.settings.mesh.internalFlow:  # if it is external flow
            bcPatches = self.settings.mesh.patches

        if name in bcPatches:
            self.settings.mesh.patches[name].type = type
            self.settings.mesh.patches[name].property = property
            IOUtils.print(f"Boundary Patch {name} changed to {type} with property {property}")
        elif name in self.settings.mesh.geometry:
            self.settings.mesh.patches[name].type = type
            self.settings.mesh.patches[name].property = property
            IOUtils.print(f"Geometry Patch {name} changed to {type} with property {property}")

        raise ValueError(f"Boundary condition {name} not found")


    def summarize_project(self):
        IOUtils.show_title("Project Summary")

        IOUtils.print(f"Internal Flow: {self.settings.mesh.internalFlow}")
        if (self.settings.mesh.internalFlow == False):
            IOUtils.print(f"On Ground: {self.settings.mesh.onGround}")
        IOUtils.print(f"Transient: {self.settings.control.transient}")
        IOUtils.print(self.settings.mesh.domain.__repr__())
        self.summarize_stl_files()

    def summarize_boundary_conditions(self):
        boundaries = []
        IOUtils.show_title("Boundary Conditions")
        IOUtils.print(f"{'No.':<5}{'Name':<20}{'Purpose':<20}{'Value':<15}")

        # Handle external flow boundary conditions first
        if not self.settings.mesh.internalFlow:
            for i, (patch_name, patch) in enumerate(self.settings.mesh.patches.items(), 1):
                IOUtils.print(f"{i:<5}{patch_name:<20}{patch.type:<20}{str(patch.property):<15}")
                boundaries.append(patch_name)

        # Handle geometry boundary conditions 
        start_i = len(boundaries) + 1
        for i, (patch_name, patch) in enumerate(self.settings.mesh.geometry.items(), start_i):
            if patch.type not in ['refinementRegion', 'refinementSurface']:
                IOUtils.print(f"{i:<5}{patch_name:<20}{patch.type:<20}{str(patch.property):<15}")
                boundaries.append(patch_name)

        return boundaries

    def summarize_stl_files(self):
        stl_files: list[str] = []
        if IOUtils.GUIMode:
            for i, (geometry_name, geometry) in enumerate(self.settings.mesh.geometry.items()):
                if isinstance(geometry, TriSurfaceMeshGeometry):
                    IOUtils.print(f"{i+1}. {geometry_name}")
                    stl_files.append(geometry_name)
            return stl_files
            
        IOUtils.show_title("STL Files")

        IOUtils.print(f"{'No.':<5}{'Name':<20}{'Purpose':<20}{'RefineMent':<15}{'Property':<15}")
        for i, (geometry_name, geometry) in enumerate(self.settings.mesh.geometry.items()):
            if isinstance(geometry, TriSurfaceMeshGeometry):
                if (geometry.property == None):
                    stl_property = "None"
                    if geometry.type == 'wall':
                        stl_property = f"nLayers: {geometry.nLayers}"
                    else:
                        stl_property = "None"
                elif isinstance(geometry.property, list):
                    stl_property = f"[{geometry.property[0]} {
                        geometry.property[1]} {geometry.property[2]}]"
                elif isinstance(geometry.property, tuple):
                    if geometry.type == 'inlet':
                        stl_property = f"U: [{geometry.property[0]} {
                            geometry.property[1]} {geometry.property[2]}]"
                    elif geometry.type == 'cellZone':
                        stl_property = f"Refinement: {geometry.property[0]}"
                else:
                    stl_property = geometry.property
                IOUtils.print(f"{i+1:<5}{geometry_name:<20}{geometry.type:<20}({geometry.refineMin} {geometry.refineMax}{')':<11}{stl_property:<15}")
                stl_files.append(geometry_name)
        IOUtils.print_line()
        return stl_files


    def get_stl_paths(self):
        stl_dir = Path(self.project_path) / "constant" / "triSurface"
        if not stl_dir.exists():
            return []
        return list(stl_dir.glob("*.stl"))