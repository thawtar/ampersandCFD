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

# This script generates the boundary conditions files for an OpenFOAM pimpleFoam simulation.
# The boundary conditions are specified in the mesh_settings.yaml file.
# This is an early version of the script and will be updated in the future.
# Brute force writing is used instead of a more elegant solution.

from pathlib import Path
from typing import Union
from ampersandCFD.models.settings import BCPatch, BoundaryConditions, SnappyHexMeshSettings, TriSurfaceMeshGeometry
from ampersandCFD.utils.generation import GenerationUtils
from ampersandCFD.utils.turbulence import TurbulenceUtils

class BoundaryConditionDictGenerator:
    @staticmethod
    def generate_u_file(mesh_settings: SnappyHexMeshSettings, boundary_conditions: BoundaryConditions):
        header = GenerationUtils.createFoamHeader(className="volVectorField", objectName="U")
        dims = GenerationUtils.createDimensions(M=0, L=1, T=-1)
        internalField = GenerationUtils.createInternalFieldVector(
            type="uniform", value=boundary_conditions.velocityInlet.u_value)
        U_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
    {
        #includeEtc "caseDicts/setConstraintTypes"
    """

        # Loop through patches for each boundary condition
        # If external flow, set the boundary conditions for blockMesh patches
        if (mesh_settings.internalFlow == False):
            for patch_name, patch in mesh_settings.patches.items():
                U_file += f"""
        {patch_name}"""
                if (isinstance(patch, BCPatch) and patch_name == 'inlet'):
                    U_file += f"""
        {{
            type {boundary_conditions.velocityInlet.u_type};
            value uniform {GenerationUtils.createTupleString(boundary_conditions.velocityInlet.u_value)};
        }}
        """
                if (isinstance(patch, BCPatch) and patch_name == 'outlet'):
                    U_file += f"""
        {{
            type {boundary_conditions.pressureOutlet.u_type};
            inletValue uniform {GenerationUtils.createTupleString(boundary_conditions.pressureOutlet.u_value)};
            value uniform {GenerationUtils.createTupleString(boundary_conditions.pressureOutlet.u_value)};
        }}
        """
                if (patch.type == 'wall'):
                    U_file += f"""
        {{
            type {boundary_conditions.wall.u_type};
            value uniform {GenerationUtils.createTupleString(boundary_conditions.wall.u_value)};
        }}
        """
                if (patch.type == 'movingWall'):
                    U_file += f"""
        {{
            type {boundary_conditions.movingWall.u_type};
            value uniform {GenerationUtils.createTupleString(boundary_conditions.movingWall.u_value)};
        }}
        """
                if (patch.type == 'symmetry'):
                    U_file += f"""
        {{
            type symmetry;
        }}
        """
        # If internal flow and half domain, set the symmetry boundary conditions
        # for the back patche
        if (mesh_settings.internalFlow and mesh_settings.halfModel):
            U_file += f"""
        back
        {{
            type symmetry;
        }}
        """
        # If internal flow, set the boundary conditions for STL patches
        for geometry_name, geometry in mesh_settings.geometry.items():
            patch_name = geometry_name.split('.')[0]
            if (isinstance(geometry, TriSurfaceMeshGeometry)):
                if (geometry.type == 'wall'):
                    U_file += f"""
        "{patch_name}.*"
        {{
            type {boundary_conditions.wall.u_type};
            value uniform {GenerationUtils.createTupleString(boundary_conditions.wall.u_value)};
        }}
        """
                elif (geometry.type == 'movingWall'):
                    U_file += f"""
        "{patch_name}.*"
        {{
            type movingWallVelocity;
            value uniform {GenerationUtils.createTupleString(boundary_conditions.wall.u_value)};
        }}
        """
                elif (geometry.type == 'inlet'):
                    U_file += f"""
        "{patch_name}.*"
        {{
            type {boundary_conditions.velocityInlet.u_type};
            value uniform {GenerationUtils.createTupleString(geometry.property)};
        }}
        """
                elif (geometry.type == 'outlet'):
                    U_file += f"""
        "{patch_name}.*"
        {{
            type {boundary_conditions.pressureOutlet.u_type};
            inletValue uniform {GenerationUtils.createTupleString(boundary_conditions.pressureOutlet.u_value)};
            value uniform {GenerationUtils.createTupleString(boundary_conditions.pressureOutlet.u_value)};
        }}
        """
                else:
                    pass
        U_file += """
    }"""
        return U_file

    @staticmethod
    def generate_p_file(mesh_settings: SnappyHexMeshSettings, boundary_conditions: BoundaryConditions):
        header = GenerationUtils.createFoamHeader(className="volScalarField", objectName="p")
        dims = GenerationUtils.createDimensions(M=0, L=2, T=-2)
        internalField = GenerationUtils.createInternalFieldScalar(
            type="uniform", value=0)
        p_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
    {
        #includeEtc "caseDicts/setConstraintTypes"
    """
        # Loop through patches for each boundary condition
        if (mesh_settings.internalFlow == False):
            for patch_name, patch in mesh_settings.patches.items():
                # print(patch)
                p_file += f"""
        {patch_name}"""
                if (isinstance(patch, BCPatch) and patch_name == 'inlet'):
                    p_file += f"""
        {{
            type {boundary_conditions.velocityInlet.p_type};
            value uniform {boundary_conditions.velocityInlet.p_value};
        }}
        """
                if (isinstance(patch, BCPatch) and patch_name == 'outlet'):
                    p_file += f"""
        {{
            type {boundary_conditions.pressureOutlet.p_type};
            value uniform {boundary_conditions.pressureOutlet.p_value};
        }}
        """
                if (patch.type == 'wall'):
                    p_file += f"""
        {{
            type {boundary_conditions.wall.p_type};
            value uniform {boundary_conditions.wall.p_value};
        }}
        """
                if (patch.type == 'movingWall'):
                    p_file += f"""
        {{
            type {boundary_conditions.movingWall.p_type};
            value uniform {boundary_conditions.movingWall.p_value};
        }}
        """
                if (patch.type == 'symmetry'):
                    p_file += f"""
        {{
            type symmetry;
        }}
        """
        # If internal flow and half domain, set the symmetry boundary conditions
        # for the back patche
        if (mesh_settings.internalFlow and mesh_settings.halfModel):
            p_file += f"""
        back
        {{
            type symmetry;
        }}
        """

        for geometry_name, geometry in mesh_settings.geometry.items():
            patch_name = geometry_name.split('.')[0]
            if (isinstance(geometry, TriSurfaceMeshGeometry)):
                if (geometry.type == 'wall'):
                    p_file += f"""
    "{patch_name}.*"
        {{
            type {boundary_conditions.wall.p_type};
            value uniform {boundary_conditions.wall.p_value};
        }}
        """
                elif (geometry.type == 'inlet'):
                    p_file += f"""
        "{patch_name}.*"
        {{
            type {boundary_conditions.velocityInlet.p_type};
            value uniform {boundary_conditions.velocityInlet.p_value};
        }}
        """
                elif (geometry.type == 'outlet'):
                    p_file += f"""
        "{patch_name}.*"
        {{
            type {boundary_conditions.pressureOutlet.p_type};
            value uniform {boundary_conditions.pressureOutlet.p_value};
        }}
        """
                else:
                    pass
        p_file += """
    }"""
        return p_file

    @staticmethod
    def generate_k_file(mesh_settings: SnappyHexMeshSettings, boundary_conditions: BoundaryConditions, nu=1.0e-5):
        header = GenerationUtils.createFoamHeader(
            className="volScalarField", objectName="k")
        dims = GenerationUtils.createDimensions(M=0, L=2, T=-2)
        internalField = GenerationUtils.createInternalFieldScalar(
            type="uniform", value=1.0e-6)
        k_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
    {
        #includeEtc "caseDicts/setConstraintTypes"
    """
        # Loop through patches for each boundary condition
        if (mesh_settings.internalFlow == False):
            for patch_name, patch in mesh_settings.patches.items():
                k_file += f"""
        {patch_name}"""
                if (isinstance(patch, BCPatch) and patch_name == 'inlet'):
                    k = TurbulenceUtils.calc_k(boundary_conditions.velocityInlet.u_value, I=0.05)
                    k_file += f"""
        {{
            type {boundary_conditions.velocityInlet.k_type};
            value uniform {k};
        }}
        """
                if (isinstance(patch, BCPatch) and patch_name == 'outlet'):
                    k_file += f"""
        {{
            type {boundary_conditions.pressureOutlet.k_type};
            value uniform {boundary_conditions.pressureOutlet.k_value};
        }}
        """
                if (patch.type == 'wall'):
                    k_file += f"""
        {{
            type {boundary_conditions.wall.k_type};
            value  {boundary_conditions.wall.k_value};
        }}
        """
                if (patch.type == 'movingWall'):
                    k_file += f"""
        {{
            type {boundary_conditions.movingWall.k_type};
            value  {boundary_conditions.movingWall.k_value};
        }}
        """
                if (patch.type == 'symmetry'):
                    k_file += f"""
        {{
            type symmetry;
        }}
        """
        # If internal flow and half domain, set the symmetry boundary conditions
        # for the back patche
        if (mesh_settings.internalFlow and mesh_settings.halfModel):
            k_file += f"""
        back
        {{
            type symmetry;
        }}
        """

        for geometry_name, geometry in mesh_settings.geometry.items():
            patch_name = geometry_name.split('.')[0]
            if (isinstance(geometry, TriSurfaceMeshGeometry)):
                if (geometry.type == 'wall'):
                    k_file += f"""
        "{patch_name}.*"
        {{
            type {boundary_conditions.wall.k_type};
            value  {boundary_conditions.wall.k_value};
        }}
        """
                elif (geometry.type == 'inlet'):
                    if (geometry.bounds != None):
                        k = TurbulenceUtils.calc_k(geometry.property, I=0.01)
                    else:
                        k = 1.0e-6  # default value
                    k_file += f"""
        "{patch_name}.*"
        {{
            type {boundary_conditions.velocityInlet.k_type};
            value uniform {k};
        }}
        """
                elif (geometry.type == 'outlet'):
                    k_file += f"""
        "{patch_name}.*"
        {{
            type {boundary_conditions.pressureOutlet.k_type};
            value uniform {boundary_conditions.pressureOutlet.k_value};
        }}
        """
                else:
                    pass

        k_file += """
    }"""
        return k_file

    @staticmethod
    def generate_omega_file(mesh_settings: SnappyHexMeshSettings, boundary_conditions: BoundaryConditions, nu=1.0e-5):
        header = GenerationUtils.createFoamHeader(
            className="volScalarField", objectName="omega")
        dims = GenerationUtils.createDimensions(M=0, L=0, T=-1)
        internalField = GenerationUtils.createInternalFieldScalar(
            type="uniform", value=1.0e-6)
        omega_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
    {
        #includeEtc "caseDicts/setConstraintTypes"
    """
        # Loop through patches for each boundary condition
        if (mesh_settings.internalFlow == False):
            for patch_name, patch in mesh_settings.patches.items():
                # print(patch)
                omega_file += f"""
        {patch_name}"""
                if (isinstance(patch, BCPatch) and patch_name == 'inlet'):

                    k = TurbulenceUtils.calc_k(boundary_conditions.velocityInlet.u_value, I=0.05)
                    nut = 100.*nu
                    omega =  k/nu*(nut/nu)**(-1)

                    omega_file += f"""
        {{
            type {boundary_conditions.velocityInlet.omega_type};
            value uniform {omega};
        }}
        """
                if (isinstance(patch, BCPatch) and patch_name == 'outlet'):
                    omega_file += f"""
        {{
            type {boundary_conditions.pressureOutlet.omega_type};
            value uniform {boundary_conditions.pressureOutlet.omega_value};
        }}
        """
                if (patch.type == 'wall'):
                    omega_file += f"""
        {{
            type {boundary_conditions.wall.omega_type};
            value  {boundary_conditions.wall.omega_value};
        }}
        """
                if (patch.type == 'movingWall'):
                    omega_file += f"""
        {{
            type {boundary_conditions.movingWall.omega_type};
            value  {boundary_conditions.movingWall.omega_value};
        }}
        """
                if (patch.type == 'symmetry'):
                    omega_file += f"""
        {{
            type symmetry;
        }}
        """

        # If internal flow and half domain, set the symmetry boundary conditions
        # for the back patche
        if (mesh_settings.internalFlow and mesh_settings.halfModel):
            omega_file += f"""
        back
        {{
            type symmetry;
        }}
        """

        for geometry_name, geometry in mesh_settings.geometry.items():
            patch_name = geometry_name.split('.')[0]
            if (isinstance(geometry, TriSurfaceMeshGeometry)):
                if (geometry.type == 'wall'):
                    omega_file += f"""
        "{patch_name}.*"
        {{
            type {boundary_conditions.wall.omega_type};
            value  {boundary_conditions.wall.omega_value};
        }}
        """
                elif (geometry.type == 'inlet'):
                    if (geometry.bounds is not None):
                        charLen = geometry.bounds.max_length
                        l = 0.07*charLen  # turbulent length scale
                        k = TurbulenceUtils.calc_k(geometry.property, I=0.01)
                        omega = 0.09**(-1./4.)*k**0.5/l
                    else:
                        omega = 1.0e-6  # default value
                    omega_file += f"""
        "{patch_name}.*"
        {{
            type {boundary_conditions.velocityInlet.omega_type};
            value uniform {omega};
        }}
        """
                elif (geometry.type == 'outlet'):
                    omega_file += f"""
        "{patch_name}.*"
        {{
            type {boundary_conditions.pressureOutlet.omega_type};
            value uniform {boundary_conditions.pressureOutlet.omega_value};
        }}
        """
                else:
                    pass

        omega_file += """
    }"""
        return omega_file

    @staticmethod
    def generate_epsilon_file(mesh_settings: SnappyHexMeshSettings, boundary_conditions: BoundaryConditions, nu=1.0e-5):
        header = GenerationUtils.createFoamHeader(
            className="volScalarField", objectName="epsilon")
        dims = GenerationUtils.createDimensions(M=0, L=2, T=-3)
        internalField = GenerationUtils.createInternalFieldScalar(
            type="uniform", value=1.0e-6)
        epsilon_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
    {
        #includeEtc "caseDicts/setConstraintTypes"
    """
        # Loop through patches for each boundary condition
        if (mesh_settings.internalFlow == False):
            for patch_name, patch in mesh_settings.patches.items():
                # print(patch)
                epsilon_file += f"""
        {patch_name}"""
                if (isinstance(patch, BCPatch) and patch_name == 'inlet'):
                    k = TurbulenceUtils.calc_k(boundary_conditions.velocityInlet.u_value, I=0.05)

                    nut = 100.*nu
                    epsilon = 0.09*k**2/nu*(nut/nu)**(-1)
                    # add epsilon boundary condition
                    epsilon_file += f"""
        {{
            type {boundary_conditions.velocityInlet.epsilon_type};
            value uniform {epsilon};
        }}
        """
                if (isinstance(patch, BCPatch) and patch_name == 'outlet'):
                    epsilon_file += f"""
        {{
            type {boundary_conditions.pressureOutlet.epsilon_type};
            value uniform {boundary_conditions.pressureOutlet.epsilon_value};
        }}
        """
                if (patch.type == 'wall'):
                    epsilon_file += f"""
        {{
            type {boundary_conditions.wall.epsilon_type};
            value  {boundary_conditions.wall.epsilon_value};
        }}
        """
                if (patch.type == 'movingWall'):
                    epsilon_file += f"""
        {{
            type {boundary_conditions.movingWall.epsilon_type};
            value  {boundary_conditions.movingWall.epsilon_value};
        }}
        """
                if (patch.type == 'symmetry'):
                    epsilon_file += f"""
        {{
            type symmetry;
        }}
        """

        # If internal flow and half domain, set the symmetry boundary conditions
        # for the back patche
        if (mesh_settings.internalFlow and mesh_settings.halfModel):
            epsilon_file += f"""
        back
        {{
            type symmetry;
        }}
        """

        for geometry_name, geometry in mesh_settings.geometry.items():
            patch_name = geometry_name.split('.')[0]
            if (isinstance(geometry, TriSurfaceMeshGeometry)):
                if (geometry.type == 'wall'):
                    epsilon_file += f"""
        "{patch_name}.*"
        {{
            type {boundary_conditions.wall.epsilon_type};
            value  {boundary_conditions.wall.epsilon_value};
        }}
        """
                elif (geometry.type == 'inlet'):
                    if (geometry.bounds != None):
                        charLen = geometry.bounds.max_length
                        l = 0.07*charLen  # turbulent length scale
                        k = TurbulenceUtils.calc_k(geometry.property, I=0.01)
                        epsilon = 0.09**(3./4.)*k**(3./2.)/l
                    else:
                        epsilon = 1.0e-6  # default value
                    epsilon_file += f"""
        "{patch_name}.*"
        {{
            type {boundary_conditions.velocityInlet.epsilon_type};
            value uniform {epsilon};
        }}
        """
                elif (geometry.type == 'outlet'):
                    epsilon_file += f"""
        "{patch_name}.*"
        {{
            type {boundary_conditions.pressureOutlet.epsilon_type};
            value uniform {boundary_conditions.pressureOutlet.epsilon_value};
        }}
        """
                else:
                    pass

        epsilon_file += """
    }"""
        return epsilon_file

    @staticmethod
    def generate_nut_file(mesh_settings: SnappyHexMeshSettings, boundary_conditions: BoundaryConditions):
        header = GenerationUtils.createFoamHeader(
            className="volScalarField", objectName="nut")
        dims = GenerationUtils.createDimensions(M=0, L=2, T=-1)
        internalField = GenerationUtils.createInternalFieldScalar(
            type="uniform", value=0)
        nut_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
    {
        #includeEtc "caseDicts/setConstraintTypes"
    """
        # Loop through patches for each boundary condition
        if (mesh_settings.internalFlow == False):
            for patch_name, patch in mesh_settings.patches.items():
                # print(patch)
                nut_file += f"""
            {patch_name}"""
                if (isinstance(patch, BCPatch) and patch_name == 'inlet'):
                    nut_file += f"""
        {{
            type {boundary_conditions.velocityInlet.nut_type};
            value uniform {boundary_conditions.velocityInlet.nut_value};
        }}
        """
                if (isinstance(patch, BCPatch) and patch_name == 'outlet'):
                    nut_file += f"""
        {{
            type {boundary_conditions.pressureOutlet.nut_type};
            value uniform {boundary_conditions.pressureOutlet.nut_value};
        }}
        """
                if (patch.type == 'wall'):
                    nut_file += f"""
        {{
            type {boundary_conditions.wall.nut_type};
            value  {boundary_conditions.wall.nut_value};
        }}
        """
                if (patch.type == 'movingWall'):
                    nut_file += f"""
        {{
            type {boundary_conditions.movingWall.nut_type};
            value  {boundary_conditions.movingWall.nut_value};
        }}
        """
                if (patch.type == 'symmetry'):
                    nut_file += f"""
        {{
            type symmetry;
        }}
        """
        # If internal flow and half domain, set the symmetry boundary conditions
        # for the back patche
        if (mesh_settings.internalFlow and mesh_settings.halfModel):
            nut_file += f"""
        back
        {{
            type symmetry;
        }}
        """

        for geometry_name, geometry in mesh_settings.geometry.items():
            patch_name = geometry_name.split('.')[0]
            if (isinstance(geometry, TriSurfaceMeshGeometry)):
                if (geometry.type == 'wall'):
                    nut_file += f"""
        "{patch_name}.*"
        {{
            type {boundary_conditions.wall.nut_type};
            value  {boundary_conditions.wall.nut_value};
        }}
        """
                elif (geometry.type == 'inlet' or geometry.type == 'outlet'):
                    nut_file += f"""
        "{patch_name}.*"
        {{
            type {boundary_conditions.velocityInlet.nut_type};
            value uniform {boundary_conditions.velocityInlet.nut_value};
        }}
        """
                else:
                    pass

        nut_file += """
    }"""

        return nut_file


    @staticmethod
    def write(mesh_settings: SnappyHexMeshSettings, boundary_conditions: BoundaryConditions, project_path: Union[str, Path]):
        u_file = BoundaryConditionDictGenerator.generate_u_file(mesh_settings, boundary_conditions)
        p_file = BoundaryConditionDictGenerator.generate_p_file(mesh_settings, boundary_conditions)
        k_file = BoundaryConditionDictGenerator.generate_k_file(mesh_settings, boundary_conditions)
        omega_file = BoundaryConditionDictGenerator.generate_omega_file(mesh_settings, boundary_conditions)
        epsilon_file = BoundaryConditionDictGenerator.generate_epsilon_file(mesh_settings, boundary_conditions)
        nut_file = BoundaryConditionDictGenerator.generate_nut_file(mesh_settings, boundary_conditions)
        
        Path(project_path, "0/U").write_text(u_file)
        Path(project_path, "0/p").write_text(p_file)
        Path(project_path, "0/k").write_text(k_file)
        Path(project_path, "0/omega").write_text(omega_file)
        Path(project_path, "0/epsilon").write_text(epsilon_file)
        Path(project_path, "0/nut").write_text(nut_file)

