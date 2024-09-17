# Default values for the constants used in the ampersandCFD library
meshSettings = {
    'name': 'meshSettings',
    'scale': 1.0,
    'domain': {'minx': -3.0,
        'maxx': 5.0,
        'miny': -1.0,
        'maxy': 1.0,
        'minz': 0.0,
        'maxz': 2.0,
        'nx': 50,
        'ny': 20,
        'nz': 20},
    
    'patches': [
        {'name': 'inlet', 'type': 'patch','faces': [0, 4, 7, 3]},
        {'name': 'outlet', 'type': 'patch','faces': [1, 5, 6, 2]},
        {'name': 'front', 'type': 'wall','faces': [0, 1, 5, 4]},
        {'name': 'back', 'type': 'wall','faces': [2, 3, 7, 6]},
        {'name': 'bottom', 'type': 'wall','faces': [0, 1, 2, 3]},
        {'name': 'top', 'type': 'wall','faces': [4, 5, 6, 7]},
    ],
    'snappyHexSteps': {'castellatedMesh': 'true',
                       'snap': 'true',
                        'addLayers': 'true'},

    'geometry': [], #[{'name': 'stl1.stl','type':'triSurfaceMesh', 'refineMin': 1, 'refineMax': 3, 
                #     'featureEdges':'true','featureLevel':3,'nLayers':3},
                #{'name': 'box','type':'searchableBox', 'min': [0, 0, 0], 'max': [1, 1, 1]}],

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
                                'allowFreeStandingZoneFaces': 'true'},

    'snapControls': {'nSmoothPatch': 3,
                        'tolerance': 2.0,
                        'nSolveIter': 100,
                        'nRelaxIter': 8,
                        'nFeatureSnapIter': 10,
                        'implicitFeatureSnap': 'false',
                        'explicitFeatureSnap': 'true',
                        'multiRegionFeatureSnap': 'false'},

    'addLayersControls': {'relativeSizes': 'true',
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
                            'minTetQuality': 1.0e-30,
                            'minVol': 1e-30,
                            'minArea': 1e-30,
                            'minTwist': 0.001,
                            'minDeterminant': 0.001,
                            'minFaceWeight': 0.01,
                            'minVolRatio': 0.01,
                            'minTriangleTwist': -1,
                            'nSmoothScale': 4,
                            'errorReduction': 0.75},
    'mergeTolerance': 1e-6,
    'debug': 0,
}


physicalProperties = {
    'name': 'physicalProperties',
    'rho': 1.0,
    'nu': 1.0e-6,
    'g': [0, 0, -9.81],
    'pRef': 0,
    'Cp': 1000,
    'thermo': 'hPolynomial',
    'Pr': 0.7,
    'TRef': 300,
    'turbulenceModel': 'kOmegaSST',
}

numericalSettings = {
    'ddtSchemes': {'default': 'Euler'},
    'gradSchemes': {'default': 'Gauss linear',
                    'grad(p)': 'Gauss linear',
                    'grad(U)': 'faceMDLimited Gauss linear 0.5',},
    'divSchemes': {'default': 'Gauss linear',
                   'div(phi,U)': 'Gauss linearUpwind grad(U)',
                   'div(phi,k)': 'Gauss upwind',
                   'div(phi,omega)': 'Gauss upwind',
                   'div(phi,epsilon)': 'Gauss upwind',
                   'div(phi,nut)': 'Gauss upwind',
                   'div(nuEff*dev(T(grad(U))))': 'Gauss linear',
                   },
    'laplacianSchemes': {'default': 'Gauss linear limited 0.5',},
    'interpolationSchemes': {'default': 'linear'},
    'snGradSchemes': {'default': 'limited 0.5',},
    'fluxRequired': {'default': 'no'},
    'wallDist': 'meshWave',
    'pimpleDict': {'nOuterCorrectors': 2, 'nCorrectors': 1, 
                   'nNonOrthogonalCorrectors': 1, 
                   'pRefCell': 0, 'pRefValue': 0},
    'relaxationFactors': {'U': 0.7, 'k': 0.7, 'omega': 0.7, 'epsilon': 0.7, 'nut': 0.7, 'p': 0.3}, 
    'simpleDict':{'nNonOrthogonalCorrectors': 2, 'consistent': 'true', 'residualControl': {'U': 1e-4, 'p': 1e-4, 'k': 1e-4, 'omega': 1e-4, 'epsilon': 1e-4, 'nut': 1e-4}},
    'potentialFlowDict':{'nonOrthogonalCorrectors': 5},
}

inletValues = {
    'U': [1, 0, 0],
    'p': 0,
    'k': 0.1,
    'omega': 1,
    'epsilon': 0.1,
    'nut': 0,
}

solverSettings = {
    'U': {'type': 'PBiCGStab',
           'preconditioner': 'DILU',
           'tolerance': 1e-05,
           'relTol': 0.01,
           'maxIter': 100,
           'nSweeps': 1,
           'nPreSweeps': 0,
           'nPostSweeps': 0},
    'p': {'type': 'PCG',
           'preconditioner': 'DIC',
           'tolerance': 1e-05,
           'relTol': 0.01,
           'maxIter': 100,
           'nSweeps': 1,
           'nPreSweeps': 0,
           'nPostSweeps': 0},
    'k': {'type': 'PBiCGStab',
           'preconditioner': 'DILU',
           'tolerance': 1e-05,
           'relTol': 0.01,
           'maxIter': 100,
           'nSweeps': 1,
           'nPreSweeps': 0,
           'nPostSweeps': 0},
    'omega': {'type': 'PBiCGStab',
           'preconditioner': 'DILU',
           'tolerance': 1e-05,
           'relTol': 0.01,
           'maxIter': 100,
           'nSweeps': 1,
           'nPreSweeps': 0,
           'nPostSweeps': 0},
    'epsilon': {'type': 'PBiCGStab',
                'preconditioner': 'DILU',
                'tolerance': 1e-05,
                'relTol': 0.01,
                'maxIter': 100,
                'nSweeps': 1,
                'nPreSweeps': 0,
                'nPostSweeps': 0},
    'nut': {'type': 'PBiCGStab',
                'preconditioner': 'DILU',
                'tolerance': 1e-05,
                'relTol': 0.01,
                'maxIter': 100,
                'nSweeps': 1,
                'nPreSweeps': 0,
                'nPostSweeps': 0},
    'Phi': {'type': 'PCG',
           'preconditioner': 'DIC',
           'tolerance': 1e-05,
           'relTol': 0.01,
           'maxIter': 100,
           'nSweeps': 1,
           'nPreSweeps': 0,
           'nPostSweeps': 0},
}


boundaryConditions = {
    'velocityInlet': 
    {'u_type': 'fixedValue','u_value': inletValues['U'],
     'p_type': 'zeroGradient','p_value': inletValues['p'],
     'k_type': 'fixedValue','k_value': inletValues['k'],
     'omega_type': 'fixedValue','omega_value': inletValues['omega'],
     'epsilon_type': 'fixedValue','epsilon_value': inletValues['epsilon'],
     'nut_type': 'calculated','nut_value': inletValues['nut']},
    
    'pressureOutlet':
    {'u_type': 'inletOutlet','u_value': [0, 0, 0],
     'p_type': 'fixedValue','p_value': 0,
     'k_type': 'zeroGradient','k_value': 1.0e-6,
     'omega_type': 'zeroGradient','omega_value': 1.0e-6,
     'epsilon_type': 'zeroGradient','epsilon_value': 1.0e-6,
     'nut_type': 'calculated','nut_value': 0},

    'wall':
    {'u_type': 'noSlip','u_value': [0, 0, 0],
     'p_type': 'zeroGradient','p_value': 0,
     'k_type': 'kqRWallFunction','k_value': '$internalField',
     'omega_type': 'omegaWallFunction','omega_value': '$internalField',
     'epsilon_type': 'epsilonWallFunction','epsilon_value': '$internalField',
     'nut_type': 'nutkWallFunction','nut_value': '$internalField'},

    'movingWall':
    {'u_type': 'movingWallVelocity','u_value': [0, 0, 0],
     'p_type': 'zeroGradient','p_value': 0,
     'k_type': 'kqRWallFunction','k_value': '$internalField',
     'omega_type': 'omegaWallFunction','omega_value': '$internalField',
     'epsilon_type': 'epsilonWallFunction','epsilon_value': '$internalField',
     'nut_type': 'nutkWallFunction','nut_value': '$internalField'},
}

simulationSettings = {
    'application': 'simpleFoam',
    'startTime': 0,
    'endTime': 1,
    'deltaT': 0.001,
    'startFrom': 'startTime',
    'stopAt': 'endTime',
    'writeControl': 'timeStep',
    'writeInterval': 100,
    'purgeWrite': 0,
    'writeFormat': 'binary',
    'writePrecision': 6,
    'writeCompression': 'off',
    'timeFormat': 'general',
    'timePrecision': 6,
    'runTimeModifiable': 'true',
    'adjustTimeStep': 'yes',
    'maxCo': 0.5,
    'functions': [],
    'libs': [],
    'allowSystemOperations': 'true',
    'runTimeControl': 'adjustableRunTime',
}

parallelSettings = {
    'numberOfSubdomains': 4,
    'method': 'scotch',
    
}

simulationFlowSettings = {
    'parallel': True,
    "snappyHexMesh": True,
    'initialize': True,
    'potentialFoam': True,
    'solver': 'simpleFoam',
    'postProc': True,
    'functionObjects': [],
}

