def create_blockMeshDict(block_coords, cell_counts):
    """
    Create a blockMeshDict for OpenFOAM.

    Parameters:
    block_coords (list): A list of eight tuples, each representing the coordinates (x, y, z) of a block corner.
    cell_counts (tuple): A tuple representing the number of cells in the x, y, and z directions (nx, ny, nz).

    Returns:
    str: The content of the blockMeshDict file as a string.
    """
    assert len(block_coords) == 8, "There must be exactly 8 block coordinates."
    assert len(cell_counts) == 3, "Cell counts must be a tuple of 3 integers (nx, ny, nz)."

    vertices_str = "\n".join([f"    ({x} {y} {z})" for x, y, z in block_coords])
    nx, ny, nz = cell_counts

    blockMeshDict = f"""/*--------------------------------*- C++ -*----------------------------------*\\
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
    class       dictionary;
    object      blockMeshDict;
}}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 1.0;

vertices
(
{vertices_str}
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({nx} {ny} {nz}) simpleGrading (1 1 1)
);

edges
(
);

patches
(
    patch inlet
    (
        (0 1 5 4)
    );
    patch outlet
    (
        (2 3 7 6)
    );
    patch bottom
    (
        (0 3 7 4)
    );
    patch top
    (
        (1 2 6 5)
    );
    patch front
    (
        (0 1 2 3)
    );
    patch back
    (
        (4 5 6 7)
    );
);

mergePatchPairs
(
);

// ************************************************************************* //
"""

    return blockMeshDict

# Example usage
block_coords = [
    (0, 0, 0),
    (1, 0, 0),
    (1, 1, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 0, 1),
    (1, 1, 1),
    (0, 1, 1)
]

cell_counts = (10, 10, 10)

block_mesh_dict_content = create_blockMeshDict(block_coords, cell_counts)

# Save to file
with open("blockMeshDict", "w") as f:
    f.write(block_mesh_dict_content)

print("blockMeshDict file created.")
