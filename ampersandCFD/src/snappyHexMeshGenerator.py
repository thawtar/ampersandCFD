from constants import meshSettings
from primitives import ampersandPrimitives
def generate_snappyHexMeshDict(meshSettings):
    """
    Create a snappyHexMeshDict for OpenFOAM.

    Parameters:
    stl_files (list): A list of STL file names.
    refinement_levels (dict): A dictionary where keys are STL file names and values are refinement levels.
    layer_counts (dict): A dictionary where keys are STL file names and values are layer counts.

    Returns:
    str: The content of the snappyHexMeshDict file as a string.
    """
    snappyHexMeshDict = f""
    trueFalse = {True: "true", False: "false"}
    header = ampersandPrimitives.createFoamHeader(className="dictionary", objectName="snappyHexMeshDict")

    steps = f"""
castellatedMesh {meshSettings['snappyHexSteps']['castellatedMesh']};
snap            {meshSettings['snappyHexSteps']['snap']};
addLayers       {meshSettings['snappyHexSteps']['addLayers']};"""

    features = ""
    refinementSurfaces = ""
    maxRefinementLevel = 1
    minRefinementRegionLevel = 2
    geometry = f"""\ngeometry\n{{"""
    for an_entry in meshSettings['geometry']:
        # For STL surfaces, featureEdges and refinementSurfaces are added
        maxRefinementLevel = max(maxRefinementLevel, an_entry['refineMax'])
        if(an_entry['type'] == 'triSurfaceMesh'):
            added_geo = f"""\n
    {an_entry['name']}
    {{
        type {an_entry['type']};
        name {an_entry['name'][:-4]};
        regions
        {{
            {an_entry['name'][:-4]}
            {{
                name {an_entry['name'][:-4]};
            }}
        }}

    }}"""
            # Add features and refinement surfaces
            if(an_entry['featureEdges']):
                features += f"""
                
        {{
            file \"{an_entry['name'][:-4]}.eMesh\";
            level {an_entry['featureLevel']};
        }}"""
                if(an_entry['purpose'] == 'patch'):
                    patchType = 'patch'
                else:
                    patchType = 'wall'
            refinementSurfaces+= f"""
        {an_entry['name'][:-4]}
        {{
            level (0 0);
            regions
            {{
                {an_entry['name'][:-4]}
                {{
                    level ({an_entry['refineMin']} {an_entry['refineMax']});
                    patchInfo
                    {{
                        type {patchType};
                    }}
                }}
            }}
            
        }}""" 

        # For searchable boxes, min and max are added
        elif(an_entry['type'] == 'searchableBox'):
            added_geo = f"""
    {an_entry['name']}
    {{
        type {an_entry['type']};
        min ({an_entry['min'][0]} {an_entry['min'][1]} {an_entry['min'][2]});
        max ({an_entry['max'][0]} {an_entry['max'][1]} {an_entry['max'][2]});
    }}"""
        geometry += added_geo
    geometry += f"""
    
}}"""

    
    refinementRegions = f""
    for an_entry in meshSettings['geometry']:
        if(an_entry['type'] == 'searchableBox'):
            refinementRegions += f"""
        {an_entry['name']}
        {{
            mode inside;
            levels ((1E15 {an_entry['refineMax']})); 
        }}"""
        elif(an_entry['type'] == 'triSurfaceMesh'):
            if(an_entry['purpose'] == 'refinementRegion'):
                refinementRegions += f"""
        {an_entry['name']}
        {{
            mode distance;
            levels ((1E-4 {an_entry['property']})); 
        }}"""
        else:
            pass
    
    castellatedMeshControls = f"""\ncastellatedMeshControls
{{
    maxLocalCells {meshSettings['castellatedMeshControls']['maxLocalCells']};
    maxGlobalCells {meshSettings['castellatedMeshControls']['maxGlobalCells']};
    minRefinementCells {meshSettings['castellatedMeshControls']['minRefinementCells']};
    maxLoadUnbalance {meshSettings['castellatedMeshControls']['maxLoadUnbalance']};
    nCellsBetweenLevels {meshSettings['castellatedMeshControls']['nCellsBetweenLevels']};
    features
    (
        {features}
    );
    refinementSurfaces
    {{
        {refinementSurfaces}
    }}
    resolveFeatureAngle {meshSettings['castellatedMeshControls']['resolveFeatureAngle']};
    refinementRegions
    {{
        {refinementRegions}
    }};
    locationInMesh ({meshSettings['castellatedMeshControls']['locationInMesh'][0]} {meshSettings['castellatedMeshControls']['locationInMesh'][1]} {meshSettings['castellatedMeshControls']['locationInMesh'][2]});
    allowFreeStandingZoneFaces {meshSettings['castellatedMeshControls']['allowFreeStandingZoneFaces']};
}}"""
    
    snapControls = f"""\nsnapControls
{{
    nSmoothPatch {meshSettings['snapControls']['nSmoothPatch']};
    tolerance {meshSettings['snapControls']['tolerance']};
    nSolveIter {meshSettings['snapControls']['nSolveIter']};
    nRelaxIter {meshSettings['snapControls']['nRelaxIter']};
    nFeatureSnapIter {meshSettings['snapControls']['nFeatureSnapIter']};
    implicitFeatureSnap {meshSettings['snapControls']['implicitFeatureSnap']};
    explicitFeatureSnap {meshSettings['snapControls']['explicitFeatureSnap']};
    multiRegionFeatureSnap {meshSettings['snapControls']['multiRegionFeatureSnap']};
}}"""
    layerControls = f"""\naddLayersControls
{{
    relativeSizes {meshSettings['addLayersControls']['relativeSizes']};
    layers
    {{"""
    for an_entry in meshSettings['geometry']:
        if(an_entry['type'] == 'triSurfaceMesh'):
            if(an_entry['purpose'] == 'wall'): # If the surface is a wall, add layers
                layerControls += f"""
            "{an_entry['name'][:-4]}.*"
            {{
                nSurfaceLayers {an_entry['nLayers']};
            }}"""
    layerControls += f"""
    }};
    expansionRatio {meshSettings['addLayersControls']['expansionRatio']};
    finalLayerThickness {meshSettings['addLayersControls']['finalLayerThickness']};
    minThickness {meshSettings['addLayersControls']['minThickness']};
    nGrow {meshSettings['addLayersControls']['nGrow']};
    featureAngle {meshSettings['addLayersControls']['featureAngle']};
    nRelaxIter {meshSettings['addLayersControls']['nRelaxIter']};
    nSmoothSurfaceNormals {meshSettings['addLayersControls']['nSmoothSurfaceNormals']};
    nSmoothNormals {meshSettings['addLayersControls']['nSmoothNormals']};
    nSmoothThickness {meshSettings['addLayersControls']['nSmoothThickness']};
    maxFaceThicknessRatio {meshSettings['addLayersControls']['maxFaceThicknessRatio']};
    maxThicknessToMedialRatio {meshSettings['addLayersControls']['maxThicknessToMedialRatio']};
    minMedianAxisAngle {meshSettings['addLayersControls']['minMedianAxisAngle']};
    minMedialAxisAngle {meshSettings['addLayersControls']['minMedianAxisAngle']};
    nBufferCellsNoExtrude {meshSettings['addLayersControls']['nBufferCellsNoExtrude']};
    nLayerIter {meshSettings['addLayersControls']['nLayerIter']};
}}"""
    meshQualityControls = f"""\nmeshQualityControls
{{
    maxNonOrtho {meshSettings['meshQualityControls']['maxNonOrtho']};
    maxBoundarySkewness {meshSettings['meshQualityControls']['maxBoundarySkewness']};
    maxInternalSkewness {meshSettings['meshQualityControls']['maxInternalSkewness']};
    maxConcave {meshSettings['meshQualityControls']['maxConcave']};
    minVol {meshSettings['meshQualityControls']['minVol']};
    minTetQuality {meshSettings['meshQualityControls']['minTetQuality']};
    minArea {meshSettings['meshQualityControls']['minArea']};
    minTwist {meshSettings['meshQualityControls']['minTwist']};
    minDeterminant {meshSettings['meshQualityControls']['minDeterminant']};
    minFaceWeight {meshSettings['meshQualityControls']['minFaceWeight']};
    minVolRatio {meshSettings['meshQualityControls']['minVolRatio']};
    minTriangleTwist {meshSettings['meshQualityControls']['minTriangleTwist']};
    nSmoothScale {meshSettings['meshQualityControls']['nSmoothScale']};
    errorReduction {meshSettings['meshQualityControls']['errorReduction']};
}}"""
    debug = f"""\ndebug {meshSettings['debug']};
mergeTolerance {meshSettings['mergeTolerance']};"""
    snappyHexMeshDict += header+steps+geometry+castellatedMeshControls+snapControls+layerControls+meshQualityControls+debug
    #print(snappyHexMeshDict)
    return snappyHexMeshDict

def write_snappyHexMeshDict(snappyHexMeshDict):
    with open('snappyHexMeshDict', 'w') as file:
        file.write(snappyHexMeshDict)
   
# Example usage
if __name__ == "__main__":
    meshSettings = ampersandPrimitives.yaml_to_dict("meshSettings.yaml")


    snappy_hex_mesh_dict_content = generate_snappyHexMeshDict(meshSettings)
    with open("snappyHexMeshDict", "w") as f:
        f.write(snappy_hex_mesh_dict_content)
    print("snappyHexMeshDict file created.")
