# This script generates the boundary conditions files for an OpenFOAM pimpleFoam simulation.
# The boundary conditions are specified in the meshSettings.yaml file.
# This is an early version of the script and will be updated in the future.
# Brute force writing is used instead of a more elegant solution.
#import yaml
from primitives import ampersandPrimitives
from constants import meshSettings, boundaryConditions, inletValues
from stlAnalysis import stlAnalysis

def write_vector_boundary_condition(patch="inlet1", purpose="inlet", property=None):
    """
    Write a vector boundary condition 
    """
    property = [str(property[0]), str(property[1]), str(property[2])]
    bc = f"""{patch} 
    {{"""
    # if the purpose is an inlet, then the velocity is specified
    if purpose == "inlet":
        # write the velocity
        bc += f"""
        type            fixedValue;
        value           uniform ({property[0]} {property[1]} {property[2]});"""
    # if the purpose is an outlet, give an inletOutlet boundary condition
    elif purpose == "outlet":
        # write the pressure
        bc += f"""
        type            inletOutlet;
        inletValue      uniform (0 0 0);
        value           uniform (0 0 0);"""
    # if the purpose is a wall, give a fixedValue boundary condition
    elif purpose == "wall":
        bc += f"""
        type            fixedValue;
        value           uniform (0 0 0);"""
    # if the purpose is a symmetry, give a symmetry boundary condition
    elif purpose == "symmetry":
        bc += f"""
        type            symmetry;"""
    else:
        raise ValueError("Invalid boundary condition type")
    bc += f"""
    }}"""
    return bc

def write_turbulence_boundary_condition(patch="inlet1", purpose="inlet", 
                                    property=None, wallFunction="kqRWallFunction"):
    """
    Write a scalar boundary condition
    """
    bc = f"""{patch} 
    {{"""
    # if the purpose is an inlet, then the fixedValue is specified
    if purpose == "inlet":
        # write the velocity
        bc += f"""
        type            fixedValue;
        value           uniform {property};"""
    # if the purpose is an outlet, give an inletOutlet boundary condition
    elif purpose == "outlet":
        # write the pressure
        bc += f"""
        type            inletOutlet;
        inletValue      uniform 0;
        value           uniform 0;"""
    # if the purpose is a wall, give a fixedValue boundary condition
    elif purpose == "wall":
        bc += f"""
        type            {wallFunction};
        value           $internalField;"""
    # if the purpose is a symmetry, give a symmetry boundary condition
    elif purpose == "symmetry":
        bc += f"""
        type            symmetry;"""
    else:
        raise ValueError("Invalid boundary condition type")
    bc += f"""
    }}"""
    return bc

def write_pressure_boundary_condition(patch="inlet1", purpose="inlet", 
                                    property=0.0):
    """
    Write a scalar boundary condition
    """
    bc = f"""{patch} 
    {{"""
    # if the purpose is an inlet, then the fixedValue is specified
    if purpose == "inlet":
        # write the velocity
        bc += f"""
        type            zeroGradient;"""
    # if the purpose is an outlet, give an inletOutlet boundary condition
    elif purpose == "outlet":
        # write the pressure
        bc += f"""
        type            fixedValue;
        value           uniform {property};""" # to define reference pressure
    # if the purpose is a wall, give a fixedValue boundary condition
    elif purpose == "wall":
        bc += f"""
        type            zeroGradient;"""
    # if the purpose is a symmetry, give a symmetry boundary condition
    elif purpose == "symmetry":
        bc += f"""
        type            symmetry;"""
    else:
        raise ValueError("Invalid boundary condition type")
    bc += f"""
    }}"""
    return bc

def create_u_file(meshSettings,boundaryConditions):
    header = ampersandPrimitives.createFoamHeader(className="volVectorField", objectName="U")
    dims = ampersandPrimitives.createDimensions(M=0,L=1,T=-1)
    internalField = ampersandPrimitives.createInternalFieldVector(type="uniform", value=boundaryConditions['velocityInlet']['u_value'])
    