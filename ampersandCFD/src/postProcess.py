from primitives import ampersandPrimitives

class postProcess:
    def __init__(self):
        pass

    @staticmethod
    def generate_post_process_script():
        cmdPostProcess = f"""#!/bin/sh
cd "${{0%/*}}" || exit                                # Run from this directory
. ${{WM_PROJECT_DIR:?}}/bin/tools/RunFunctions        # Tutorial run functions
#-----------------------------------------------------
"""
        cmdPostProcess += f"""
runApplication postProcess 
"""
        return cmdPostProcess
    
    @staticmethod
    # function object for showing minimum and maximum values of the fields
    def FO_min_max():
        FO = f"""
minMax
{{
    type        fieldMinMax;
    libs        ("fieldFunctionObjects");
    writeControl timeStep;
    ;
    fields
    (
        U
        p
    );
}}"""
        return FO
    
    @staticmethod
    def FO_yPlus():
        FO = f"""
yPlus1
{{
    // Mandatory entries
    type            yPlus;
    libs            (fieldFunctionObjects);
}}
"""
        return FO
    
    @staticmethod
    def FO_forces(patchName="patchName",rhoInf=1,CofR=(0,0,0),pitchAxis=(0,1,0)):
        FO = f"""
forces
{{
    type            forces;
    libs            (forces);
    writeControl    timeStep;
    timeInterval    1;
    patches         ({patchName});
    rho             rhoInf;      // Indicates incompressible
    rhoInf          {rhoInf};           // Required when rho = rhoInf
    CofR            ({CofR[0]} {CofR[1]} {CofR[2]});  // Centre of rotation, used for moment calculation
    pitchAxis       ({pitchAxis[0]} {pitchAxis[1]} {pitchAxis[2]});  // Pitch axis
}}
"""
        return FO
    
