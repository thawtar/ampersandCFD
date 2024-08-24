def create_boundary_conditions(case_directory, boundary_conditions):
    """
    Create boundary condition files for an OpenFOAM pimpleFoam simulation.

    Parameters:
    case_directory (str): Path to the case directory.
    boundary_conditions (dict): Dictionary specifying boundary conditions for U, p, k, and omega.
    """
    # Create directory for time step 0
    import os

    time_step_0_dir = os.path.join(case_directory, "0")
    os.makedirs(time_step_0_dir, exist_ok=True)

    def write_file(file_path, content):
        with open(file_path, "w") as f:
            f.write(content)

    def generate_U_file(bc):
        return f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2012                                 |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
/*  This file is part of OpenFOAM.                                            *
 *                                                                            *
 *  OpenFOAM is free software: you can redistribute it and/or modify it       *
 *  under the terms of the GNU General Public License as published by the     *
 *  Free Software Foundation, either version 3 of the License, or             *
 *  (at your option) any later version.                                       *
 *                                                                            *
 *  OpenFOAM is distributed in the hope that it will be useful, but WITHOUT   *
 *  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or     *
 *  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License     *
 *  for more details.                                                         *
 *                                                                            *
 *  You should have received a copy of the GNU General Public License         *
 *  along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.         *
\\*---------------------------------------------------------------------------*/

FoamFile
{{
    version     2.0;
    format      ascii;
    class       volVectorField;
    location    "0";
    object      U;
}}

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{{
    {bc['U']}
}}

// ************************************************************************* //
"""

    def generate_p_file(bc):
        return f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2012                                 |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
/*  This file is part of OpenFOAM.                                            *
 *                                                                            *
 *  OpenFOAM is free software: you can redistribute it and/or modify it       *
 *  under the terms of the GNU General Public License as published by the     *
 *  Free Software Foundation, either version 3 of the License, or             *
 *  (at your option) any later version.                                       *
 *                                                                            *
 *  OpenFOAM is distributed in the hope that it will be useful, but WITHOUT   *
 *  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or     *
 *  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License     *
 *  for more details.                                                         *
 *                                                                            *
 *  You should have received a copy of the GNU General Public License         *
 *  along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.         *
\\*---------------------------------------------------------------------------*/

FoamFile
{{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      p;
}}

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{{
    {bc['p']}
}}

// ************************************************************************* //
"""

    def generate_k_file(bc):
        return f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2012                                 |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
/*  This file is part of OpenFOAM.                                            *
 *                                                                            *
 *  OpenFOAM is free software: you can redistribute it and/or modify it       *
 *  under the terms of the GNU General Public License as published by the     *
 *  Free Software Foundation, either version 3 of the License, or             *
 *  (at your option) any later version.                                       *
 *                                                                            *
 *  OpenFOAM is distributed in the hope that it will be useful, but WITHOUT   *
 *  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or     *
 *  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License     *
 *  for more details.                                                         *
 *                                                                            *
 *  You should have received a copy of the GNU General Public License         *
 *  along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.         *
\\*---------------------------------------------------------------------------*/

FoamFile
{{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      k;
}}

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0.1;

boundaryField
{{
    {bc['k']}
}}

// ************************************************************************* //
"""

    def generate_omega_file(bc):
        return f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2012                                 |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
/*  This file is part of OpenFOAM.                                            *
 *                                                                            *
 *  OpenFOAM is free software: you can redistribute it and/or modify it       *
 *  under the terms of the GNU General Public License as published by the     *
 *  Free Software Foundation, either version 3 of the License, or             *
 *  (at your option) any later version.                                       *
 *                                                                            *
 *  OpenFOAM is distributed in the hope that it will be useful, but WITHOUT   *
 *  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or     *
 *  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License     *
 *  for more details.                                                         *
 *                                                                            *
 *  You should have received a copy of the GNU General Public License         *
 *  along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.         *
\\*---------------------------------------------------------------------------*/

FoamFile
{{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      omega;
}}

dimensions      [0 0 -1 0 0 0 0];

internalField   uniform 1;

boundaryField
{{
    {bc['omega']}
}}

// ************************************************************************* //
"""

   
