#from constants import parallelSettings
from primitives import ampersandPrimitives

def createDecomposeParDict(parallelSettings):
    decomposeParDict = ampersandPrimitives.createFoamHeader(className='dictionary', objectName='decomposeParDict')
    decomposeParDict += f"""
numberOfSubdomains {parallelSettings['numberOfSubdomains']};
method {parallelSettings['method']};
"""
    return decomposeParDict
    