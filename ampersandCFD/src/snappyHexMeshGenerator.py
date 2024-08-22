def create_snappyHexMeshDict(stl_files, refinement_levels, layer_counts):
    """
    Create a snappyHexMeshDict for OpenFOAM.

    Parameters:
    stl_files (list): A list of STL file names.
    refinement_levels (dict): A dictionary where keys are STL file names and values are refinement levels.
    layer_counts (dict): A dictionary where keys are STL file names and values are layer counts.

    Returns:
    str: The content of the snappyHexMeshDict file as a string.
    """
    stl_entries = "\n".join([
        f"""
        {stl_file}
        {{
            type triSurfaceMesh;
            name {stl_file.split('.')[0]};
        }}
        """ for stl_file in stl_files
    ])

    refinement_surfaces_entries = "\n".join([
        f"""
        {stl_file.split('.')[0]}
        {{
            level ({refinement_levels[stl_file]} {refinement_levels[stl_file]});
        }}
        """ for stl_file in stl_files
    ])

    layers_entries = "\n".join([
        f"""
        {stl_file.split('.')[0]}
        {{
            nSurfaceLayers {layer_counts[stl_file]};
        }}
        """ for stl_file in stl_files
    ])

    snappyHexMeshDict = f"""/*--------------------------------*- C++ -*----------------------------------*\\
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
    object      snappyHexMeshDict;
}}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

castellatedMesh true;
snap            true;
addLayers       true;

geometry
(
{stl_entries}
);

castellatedMeshControls
{{
    maxLocalCells 1000000;
    maxGlobalCells 2000000;
    minRefinementCells 10;
    maxLoadUnbalance 0.10;
    nCellsBetweenLevels 3;

    features
    (
        // no features specified
    );

    refinementSurfaces
    (
{refinement_surfaces_entries}
    );

    resolveFeatureAngle 30;

    refinementRegions
    {{
        // no regions specified
    }};

    locationInMesh (0 0 0);

    allowFreeStandingZoneFaces true;
}}

snapControls
{{
    nSmoothPatch 3;
    tolerance 2.0;
    nSolveIter 30;
    nRelaxIter 5;
    nFeatureSnapIter 10;
    implicitFeatureSnap false;
    explicitFeatureSnap true;
    multiRegionFeatureSnap false;
}}

addLayersControls
{{
    relativeSizes true;
    layers
    {{
{layers_entries}
    }};

    expansionRatio 1.0;
    finalLayerThickness 0.3;
    minThickness 0.1;
    nGrow 0;
    featureAngle 30;
    nRelaxIter 5;
    nSmoothSurfaceNormals 1;
    nSmoothNormals 3;
    nSmoothThickness 10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedianAxisAngle 90;
    nBufferCellsNoExtrude 0;
    nLayerIter 50;
}}

meshQualityControls
{{
    maxNonOrtho 65;
    maxBoundarySkewness 20;
    maxInternalSkewness 4;
    maxConcave 80;
    minVol 1e-13;
    minTetQuality 1e-30;
    minArea -1;
    minTwist 0.02;
    minDeterminant 0.001;
    minFaceWeight 0.05;
    minVolRatio 0.01;
    minTriangleTwist -1;

    nSmoothScale 4;
    errorReduction 0.75;
}}

debug 0;
mergeTolerance 1e-6;

// ************************************************************************* //
"""

    return snappyHexMeshDict

# Example usage
stl_files = ["geometry1.stl", "geometry2.stl"]
refinement_levels = {
    "geometry1.stl": 3,
    "geometry2.stl": 4
}
layer_counts = {
    "geometry1.stl": 3,
    "geometry2.stl": 2
}

snappy_hex_mesh_dict_content = create_snappyHexMeshDict(stl_files, refinement_levels, layer_counts)

# Save to file
with open("snappyHexMeshDict", "w") as f:
    f.write(snappy_hex_mesh_dict_content)

print("snappyHexMeshDict file created.")
