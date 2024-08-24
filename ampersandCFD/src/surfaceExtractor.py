import yaml
from primitives import ampersandPrimitives
from constants import meshSettings

def create_surfaceFeatureExtractDict(meshSettings):
    header = ampersandPrimitives.createFoamHeader(className="dictionary", objectName="surfaceFeatureExtractDict")
    surfaceFeatureExtractDict = f""+header
    for anEntry in meshSettings['geometry']:
        if anEntry['type'] == 'triSurfaceMesh':
            surfaceFeature = f"""\n{anEntry['name']}
{{
    extractionMethod    extractFromSurface; 
    includedAngle   170;
    subsetFeatures
    {{
        nonManifoldEdges       no;
        openEdges       yes;
    }}
    writeObj            yes;
    writeSets           no;
}}"""
            surfaceFeatureExtractDict += surfaceFeature
    

    return surfaceFeatureExtractDict
if __name__ == "__main__":
    meshSettings = ampersandPrimitives.yaml_to_dict('meshSettings.yaml')
    surfaceFeatureExtractDict = create_surfaceFeatureExtractDict(meshSettings)
    #print(surfaceFeatureExtractDict)
    with open('surfaceFeatureExtractDict', 'w') as file:
        file.write(surfaceFeatureExtractDict)