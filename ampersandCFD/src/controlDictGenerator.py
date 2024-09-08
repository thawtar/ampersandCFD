from constants import meshSettings, physicalProperties, numericalSettings, inletValues, boundaryConditions
from primitives import ampersandPrimitives
from constants import simulationSettings

def createControlDict(simulationSettings):
    controlDict = ampersandPrimitives.createFoamHeader(className='dictionary', objectName='controlDict')
    controlDict += f"""
application     {simulationSettings['application']};
startFrom       {simulationSettings['startFrom']};
startTime       {simulationSettings['startTime']};
stopAt          {simulationSettings['stopAt']};
endTime         {simulationSettings['endTime']};
deltaT          {simulationSettings['deltaT']};
writeControl    {simulationSettings['writeControl']};
writeInterval   {simulationSettings['writeInterval']};
purgeWrite      {simulationSettings['purgeWrite']};
writeFormat     {simulationSettings['writeFormat']};
writePrecision  {simulationSettings['writePrecision']};
writeCompression {simulationSettings['writeCompression']};
timeFormat      {simulationSettings['timeFormat']};
timePrecision   {simulationSettings['timePrecision']};
runTimeModifiable {simulationSettings['runTimeModifiable']};
adjustTimeStep  {simulationSettings['adjustTimeStep']};
maxCo           {simulationSettings['maxCo']};
functions
{{
}};
libs
(
);
"""
    return controlDict


# Generate controlDict
if __name__ == '__main__':
    controlDict = createControlDict(simulationSettings)
    print(controlDict)