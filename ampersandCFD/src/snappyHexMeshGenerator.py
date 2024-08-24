from constants import meshSettings
from primitives import ampersandPrimitives
def create_snappyHexMeshDict(meshSettings):
    """
    Create a snappyHexMeshDict for OpenFOAM.

    Parameters:
    stl_files (list): A list of STL file names.
    refinement_levels (dict): A dictionary where keys are STL file names and values are refinement levels.
    layer_counts (dict): A dictionary where keys are STL file names and values are layer counts.

    Returns:
    str: The content of the snappyHexMeshDict file as a string.
    """

    trueFalse = {True: "true", False: "false"}
    header = ampersandPrimitives.createFoamHeader(className="dictionary", objectName="snappyHexMeshDict")

    steps = f"""castellatedMesh {trueFalse[meshSettings['snappyHexSteps']['castellatedMesh']]};
    snap            {trueFalse[meshSettings['snappyHexSteps']['snap']]};
    addLayers       {trueFalse[meshSettings['snappyHexSteps']['addLayers']]};"""
    
    geometry = f"geometry"
    for an_entry in meshSettings['geometry']:
        geometry += f"""
    
    {an_entry['name']}
    {{
        type {an_entry['type']};
        name {an_entry['name'][:-4]};
        
    }}
    ;"""

    print(header+steps)
    exit(0)
    snappyHexMeshDict = header+f"""/*--------------------------------*- C++ -*----------------------------------*\\


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

castellatedMesh {meshSettings['castellatedMesh']};
snap            {meshSettings['snap']};
addLayers       {meshSettings['addLayers']};

geometry
(
{stl_entries}
);

castellatedMeshControls
{{
    maxLocalCells {meshSettings['maxLocalCells']};
    maxGlobalCells {meshSettings['maxGlobalCells']};
    minRefinementCells {meshSettings['minRefinementCells']};
    maxLoadUnbalance {meshSettings['maxLoadUnbalance']};
    nCellsBetweenLevels {meshSettings['nCellsBetweenLevels']};

    features
    (
        // no features specified
    );

    refinementSurfaces
    (
{refinement_surfaces_entries}
    );

    resolveFeatureAngle {meshSettings['resolveFeatureAngle']};

    refinementRegions
    {{
        // no regions specified
    }};

    locationInMesh (0 0 0);

    allowFreeStandingZoneFaces {meshSettings['allowFreeStandingZoneFaces']};
}}

snapControls
{{
    nSmoothPatch {meshSettings['nSmoothPatch']};
    tolerance {meshSettings['tolerance']};
    nSolveIter {meshSettings['nSolveIter']};
    nRelaxIter {meshSettings['nRelaxIter']};
    nFeatureSnapIter {meshSettings['nFeatureSnapIter']};
    implicitFeatureSnap {meshSettings['implicitFeatureSnap']};
    explicitFeatureSnap {meshSettings['explicitFeatureSnap']};
    multiRegionFeatureSnap {meshSettings['multiRegionFeatureSnap']};
}}

addLayersControls
{{
    relativeSizes {meshSettings['relativeSizes']};
    layers
    {{
{layers_entries}
    }};

    expansionRatio {meshSettings['expansionRatio']};
    finalLayerThickness {meshSettings['finalLayerThickness']};
    minThickness {meshSettings['minThickness']};
    nGrow {meshSettings['nGrow']};
    featureAngle {meshSettings['featureAngle']};
    nRelaxIter {meshSettings['nRelaxIter']};
    nSmoothSurfaceNormals {meshSettings['nSmoothSurfaceNormals']};
    nSmoothNormals {meshSettings['nSmoothNormals']};
    nSmoothThickness {meshSettings['nSmoothThickness']};
    maxFaceThicknessRatio {meshSettings['maxFaceThicknessRatio']};
    maxThicknessToMedialRatio {meshSettings['maxThicknessToMedialRatio']};
    minMedianAxisAngle {meshSettings['minMedianAxisAngle']};
    nBufferCellsNoExtrude {meshSettings['nBufferCellsNoExtrude']};
    nLayerIter {meshSettings['nLayerIter']};
}}

meshQualityControls
{{
    maxNonOrtho {meshSettings['maxNonOrtho']};
    maxBoundarySkewness {meshSettings['maxBoundarySkewness']};
    maxInternalSkewness {meshSettings['maxInternalSkewness']};
    maxConcave {meshSettings['maxConcave']};
    minVol {meshSettings['minVol']};
    minTetQuality {meshSettings['minTetQuality']};
    minArea {meshSettings['minArea']};
    minTwist {meshSettings['minTwist']};
    minDeterminant {meshSettings['minDeterminant']};
    minFaceWeight {meshSettings['minFaceWeight']};
    minVolRatio {meshSettings['minVolRatio']};
    minTriangleTwist {meshSettings['minTriangleTwist']};

    nSmoothScale {meshSettings['nSmoothScale']};
    errorReduction {meshSettings['errorReduction']};
}}

debug {meshSettings['debug']};
mergeTolerance {meshSettings['mergeTolerance']};

// ************************************************************************* //
"""

    return snappyHexMeshDict
# aaa
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

snappy_hex_mesh_dict_content = create_snappyHexMeshDict(meshSettings)


