# backend module for the ampersandCFD project
# Description: This file contains the code to generate OpenFOAM files

import os
import yaml
from primitives import ampersandPrimitives



class ampersandEngine: # ampersandEngine class to handle the generation of OpenFOAM files
    # this class will contain the methods to handle the logic and program flow
    def __init__(self):
        pass
    


# Example dictionary
meshSettings = {
    'name': 'meshSettings',
    'domain': {'minx': 0.0,
        'maxx': 1.0,
        'miny': 0.0,
        'maxy': 1.0,
        'minz': 0.0,
        'maxz': 1.0,
        'nx': 10,
        'ny': 10,
        'nz': 10},
    
    'patches': [
        {'left': 'inlet', 'type': 'patch'},
        {'right': 'outlet', 'type': 'patch'},
        {'front': 'front', 'type': 'wall'},
        {'back': 'back', 'type': 'wall'},
        {'bottom': 'bottom', 'type': 'wall'},
        {'top': 'top', 'type': 'wall'}
    ],
    'locationInMesh': {'x': 0.5, 'y': 0.5, 'z': 0.5},
    'snappyHexSteps': {'castellatedMesh': True,
                       'snap': True,
                        'addLayers': True},

    'stl_entries': [{'name': 'stl1.stl', 'refineMin': 1, 'refineMax': 3, 
                     'featureEdges':True,'nLayers':3},],

    'castellatedMeshControls': {'maxLocalCells': 2_000_000,
                                'maxGlobalCells': 5_000_000,
                                'minRefinementCells': 5,
                                'maxLoadUnbalance': 0.10,
                                'nCellsBetweenLevels': 5,
                                'features': [],
                                'refinementSurfaces': [],
                                'resolveFeatureAngle': 30,
                                'refinementRegions': [],
                                'locationInMesh': [0, 0, 0],
                                'allowFreeStandingZoneFaces': True},

    'snapControls': {'nSmoothPatch': 3,
                        'tolerance': 2.0,
                        'nSolveIter': 100,
                        'nRelaxIter': 8,
                        'nFeatureSnapIter': 10,
                        'implicitFeatureSnap': False,
                        'explicitFeatureSnap': True,
                        'multiRegionFeatureSnap': False},

    'addLayersControls': {'relativeSizes': True,
                            'expansionRatio': 1.2,
                            'finalLayerThickness': 0.3,
                            'minThickness': 0.001,
                            'nGrow': 0,
                            'featureAngle': 180,
                            'nRelaxIter': 5,
                            'nSmoothSurfaceNormals': 1,
                            'nSmoothNormals': 3,
                            'nSmoothThickness': 10,
                            'maxFaceThicknessRatio': 0.5,
                            'maxThicknessToMedialRatio': 0.3,
                            'minMedianAxisAngle': 90,
                            'nBufferCellsNoExtrude': 0,
                            'nLayerIter': 10,
                            'nRelaxIter': 5},

    'meshQualityControls': {'maxNonOrtho': 75,
                            'maxBoundarySkewness': 4,
                            'maxInternalSkewness': 4,
                            'maxConcave': 180,
                            'minTetQuality': 0.5,
                            'minVol': 1e-30,
                            'minArea': 1e-30,
                            'minTwist': 0.001,
                            'minDeterminant': 0.001,
                            'minFaceWeight': 0.01,
                            'minVolRatio': 0.01,
                            'minTriangleTwist': -1},
}


if __name__ == '__main__':
    # Specify the output YAML file
    output_file = 'meshSettings.yaml'

    # Convert the dictionary to a YAML file
    ampersandPrimitives.dict_to_yaml(meshSettings, output_file)

    dict_ = ampersandPrimitives.yaml_to_dict(output_file)
    print(dict_)

