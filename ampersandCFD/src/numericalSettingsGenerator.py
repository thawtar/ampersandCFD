from constants import numericalSettings, solverSettings
from primitives import ampersandPrimitives

def create_algorithmDict(numericalSettings):
    header = ampersandPrimitives.createFoamHeader(className="dictionary", objectName="pimpleDict")
    algorithmDict = f""+header
    algorithmDict += f"""
    PIMPLE
    {{
        nOuterCorrectors {numericalSettings['pimpleDict']['nOuterCorrectors']};
        nCorrectors {numericalSettings['pimpleDict']['nCorrectors']};
        nNonOrthogonalCorrectors {numericalSettings['pimpleDict']['nNonOrthogonalCorrectors']};
        pRefCell {numericalSettings['pimpleDict']['pRefCell']};
        pRefValue {numericalSettings['pimpleDict']['pRefValue']};
    }}
    SIMPLE
    {{
        nNonOrthogonalCorrectors {numericalSettings['simpleDict']['nNonOrthogonalCorrectors']};
        consistent {numericalSettings['simpleDict']['consistent']};
        residualControl
        {{
            U {numericalSettings['simpleDict']['residualControl']['U']};
            p {numericalSettings['simpleDict']['residualControl']['p']};
            k {numericalSettings['simpleDict']['residualControl']['k']};
            omega {numericalSettings['simpleDict']['residualControl']['omega']};
            epsilon {numericalSettings['simpleDict']['residualControl']['epsilon']};
            nut {numericalSettings['simpleDict']['residualControl']['nut']};
        }}
    }}
    potentialFlow
    {{
        nonOrthogonalCorrectors {numericalSettings['potentialFlowDict']['nonOrthogonalCorrectors']};
    }}
    relaxationFactors
    {{
        equations
        {{
            U {numericalSettings['relaxationFactors']['U']};
            
            k {numericalSettings['relaxationFactors']['k']};
            omega {numericalSettings['relaxationFactors']['omega']};
            epsilon {numericalSettings['relaxationFactors']['epsilon']};
            nut {numericalSettings['relaxationFactors']['nut']};
        }}
        fields
        {{
            p {numericalSettings['relaxationFactors']['p']};
        }}
    }}
    """
    return algorithmDict

def create_solverDict(solverSettings,solverName="U"):
    #header = ampersandPrimitives.createFoamHeader(className="dictionary", objectName="solver")
    solverDict = f""
    solverDict += f"""
    {solverName}
    {{
        solver {solverSettings[solverName]['type']};
        preconditioner {solverSettings[solverName]['preconditioner']};
        tolerance {solverSettings[solverName]['tolerance']};
        relTol {solverSettings[solverName]['relTol']};
        maxIter {solverSettings[solverName]['maxIter']};
        nSweeps {solverSettings[solverName]['nSweeps']};
        nPreSweeps {solverSettings[solverName]['nPreSweeps']};
    }}
    """
    return solverDict

def create_fvSolutionDict(numericalSettings,solverSettings):
    header = ampersandPrimitives.createFoamHeader(className="dictionary", objectName="fvSolution")
    fvSolutionDict = f""+header
    fvSolutionDict += f"""
    solvers
    {{
    """
    for solver in solverSettings.keys():
        fvSolutionDict += create_solverDict(solverSettings,solver)
    fvSolutionDict += f"""
    }}
    """
    fvSolutionDict += create_algorithmDict(numericalSettings)
    return fvSolutionDict

def create_fvSchemesDict(numericalSettings):
    header = ampersandPrimitives.createFoamHeader(className="dictionary", objectName="fvSchemes")
    fvSchemesDict = f""+header
    fvSchemesDict += f"""
ddtSchemes
{{
    default {numericalSettings['ddtSchemes']['default']};
}}
gradSchemes
{{
    default {numericalSettings['gradSchemes']['default']};
    grad(p) {numericalSettings['gradSchemes']['grad(p)']};
    grad(U) {numericalSettings['gradSchemes']['grad(U)']};
}}
divSchemes
{{
    default {numericalSettings['divSchemes']['default']};
    div(phi,U) {numericalSettings['divSchemes']['div(phi,U)']}; 
    div(phi,k) {numericalSettings['divSchemes']['div(phi,k)']};
    div(phi,omega) {numericalSettings['divSchemes']['div(phi,omega)']};
    div(phi,epsilon) {numericalSettings['divSchemes']['div(phi,epsilon)']};
    div(phi,nut) {numericalSettings['divSchemes']['div(phi,nut)']};
    div(nuEff*dev(T(grad(U)))) {numericalSettings['divSchemes']['div(nuEff*dev(T(grad(U))))']};
}}
laplacianSchemes
{{
    default {numericalSettings['laplacianSchemes']['default']};
}}
interpolationSchemes
{{
    default {numericalSettings['interpolationSchemes']['default']};
}}
snGradSchemes
{{
    default {numericalSettings['snGradSchemes']['default']};
}}
fluxRequired
{{
    default {numericalSettings['fluxRequired']['default']};
}}
wallDist
{{
    method {numericalSettings['wallDist']};
}}
"""
    return fvSchemesDict

