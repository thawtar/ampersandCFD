# This script generates the boundary conditions files for an OpenFOAM pimpleFoam simulation.
# The boundary conditions are specified in the meshSettings.yaml file.
# This is an early version of the script and will be updated in the future.
# Brute force writing is used instead of a more elegant solution.
#import yaml
from primitives import ampersandPrimitives
from constants import meshSettings, boundaryConditions, inletValues



def tuple_to_string(t):
    return f"({t[0]} {t[1]} {t[2]})"

def create_u_file(meshSettings,boundaryConditions):
    header = ampersandPrimitives.createFoamHeader(className="volVectorField", objectName="U")
    dims = ampersandPrimitives.createDimensions(M=0,L=1,T=-1)
    internalField = ampersandPrimitives.createInternalFieldVector(type="uniform", value=boundaryConditions['velocityInlet']['u_value'])
    U_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
{"""
    # Loop through patches for each boundary condition
    for patch in meshSettings['patches']:
        U_file += f"""
    {patch['name']}"""
        if(patch['type'] == 'patch' and patch['name'] == 'inlet'):
            U_file += f"""
    {{
        type {boundaryConditions['velocityInlet']['u_type']};
        value uniform {tuple_to_string(boundaryConditions['velocityInlet']['u_value'])};
    }}
    """
        if(patch['type'] == 'patch' and patch['name'] == 'outlet'):
            U_file += f"""
    {{
        type {boundaryConditions['pressureOutlet']['u_type']};
        inletValue uniform {tuple_to_string(boundaryConditions['pressureOutlet']['u_value'])};
        value uniform {tuple_to_string(boundaryConditions['pressureOutlet']['u_value'])};
    }}
    """
        if(patch['type'] == 'wall'):
            U_file += f"""
    {{
        type {boundaryConditions['wall']['u_type']};
        value uniform {tuple_to_string(boundaryConditions['wall']['u_value'])};
    }}
    """
        if(patch['type'] == 'movingWall'):
            U_file += f"""
    {{
        type {boundaryConditions['movingWall']['u_type']};
        value uniform {tuple_to_string(boundaryConditions['movingWall']['u_value'])};
    }}
    """
    for patch in meshSettings['geometry']:
        if(patch['type'] == 'triSurfaceMesh'):
            if(patch['purpose'] == 'wall'):
                U_file += f"""
    "{patch['name'][:-4]}.*"
    {{
        type {boundaryConditions['wall']['u_type']};
        value uniform {tuple_to_string(boundaryConditions['wall']['u_value'])};
    }}
    """
            elif(patch['purpose'] == 'inlet'):
                U_file += f"""
    "{patch['name'][:-4]}.*"
    {{
        type {boundaryConditions['wall']['u_type']};
        value uniform {tuple_to_string(patch['property'])};
    }}
    """  
            elif(patch['purpose'] == 'outlet'):
                U_file += f"""
    "{patch['name'][:-4]}.*"
    {{
        type {boundaryConditions['pressureOutlet']['u_type']};
        inletValue uniform {tuple_to_string(boundaryConditions['pressureOutlet']['u_value'])};
        value uniform {tuple_to_string(boundaryConditions['pressureOutlet']['u_value'])};
    }}
    """
            else:
                pass         
    U_file += """
}"""
    return U_file

def create_p_file(meshSettings,boundaryConditions):
    header = ampersandPrimitives.createFoamHeader(className="volScalarField", objectName="p")
    dims = ampersandPrimitives.createDimensions(M=0,L=2,T=-2)
    internalField = ampersandPrimitives.createInternalFieldScalar(type="uniform", value=0)
    p_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
{"""
    # Loop through patches for each boundary condition
    for patch in meshSettings['patches']:
        #print(patch)
        p_file += f"""
    {patch['name']}"""
        if(patch['type'] == 'patch' and patch['name'] == 'inlet'):
            p_file += f"""
    {{
        type {boundaryConditions['velocityInlet']['p_type']};
        value uniform {boundaryConditions['velocityInlet']['p_value']};
    }}
    """
        if(patch['type'] == 'patch' and patch['name'] == 'outlet'):
            p_file += f"""
    {{
        type {boundaryConditions['pressureOutlet']['p_type']};
        value uniform {boundaryConditions['pressureOutlet']['p_value']};
    }}
    """
        if(patch['type'] == 'wall'):
            p_file += f"""
    {{
        type {boundaryConditions['wall']['p_type']};
        value uniform {boundaryConditions['wall']['p_value']};
    }}
    """
        if(patch['type'] == 'movingWall'):
            p_file += f"""
    {{
        type {boundaryConditions['movingWall']['p_type']};
        value uniform {boundaryConditions['movingWall']['p_value']};
    }}
    """
    for patch in meshSettings['geometry']:
        if(patch['type'] == 'triSurfaceMesh'):
            if(patch['purpose'] == 'wall'):
                p_file += f"""
   "{patch['name'][:-4]}.*"
    {{
        type {boundaryConditions['wall']['p_type']};
        value uniform {boundaryConditions['wall']['p_value']};
    }}
    """
            elif(patch['purpose'] == 'inlet'):
                p_file += f"""
    "{patch['name'][:-4]}.*"
    {{
        type {boundaryConditions['velocityInlet']['p_type']};
        value uniform {boundaryConditions['velocityInlet']['p_value']};
    }}
    """  
            elif(patch['purpose'] == 'outlet'):
                p_file += f"""
    "{patch['name'][:-4]}.*"
    {{
        type {boundaryConditions['pressureOutlet']['p_type']};
        value uniform {boundaryConditions['pressureOutlet']['p_value']};
    }}
    """
            else:
                pass 
    p_file += """
}"""
    return p_file

def create_k_file(meshSettings,boundaryConditions):
    header = ampersandPrimitives.createFoamHeader(className="volScalarField", objectName="k")
    dims = ampersandPrimitives.createDimensions(M=0,L=2,T=-2)
    internalField = ampersandPrimitives.createInternalFieldScalar(type="uniform", value=1.0e-6)
    k_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
{"""
    # Loop through patches for each boundary condition
    for patch in meshSettings['patches']:
        #print(patch)
        k_file += f"""
    {patch['name']}"""
        if(patch['type'] == 'patch' and patch['name'] == 'inlet'):
            k_file += f"""
    {{
        type {boundaryConditions['velocityInlet']['k_type']};
        value uniform {boundaryConditions['velocityInlet']['k_value']};
    }}
    """
        if(patch['type'] == 'patch' and patch['name'] == 'outlet'):
            k_file += f"""
    {{
        type {boundaryConditions['pressureOutlet']['k_type']};
        value uniform {boundaryConditions['pressureOutlet']['k_value']};
    }}
    """
        if(patch['type'] == 'wall'):
            k_file += f"""
    {{
        type {boundaryConditions['wall']['k_type']};
        value  {boundaryConditions['wall']['k_value']};
    }}
    """
        if(patch['type'] == 'movingWall'):
            k_file += f"""
    {{
        type {boundaryConditions['movingWall']['k_type']};
        value  {boundaryConditions['movingWall']['k_value']};
    }}
    """
    for patch in meshSettings['geometry']:
        if(patch['type'] == 'triSurfaceMesh'):
            if(patch['purpose'] == 'wall'):
                k_file += f"""
    "{patch['name'][:-4]}.*"
    {{
        type {boundaryConditions['wall']['k_type']};
        value  {boundaryConditions['wall']['k_value']};
    }}
    """
            elif(patch['purpose'] == 'inlet'):
                k_file += f"""
    "{patch['name'][:-4]}.*"
    {{
        type {boundaryConditions['velocityInlet']['k_type']};
        value uniform {boundaryConditions['velocityInlet']['k_value']};
    }}
    """  
            elif(patch['purpose'] == 'outlet'):
                k_file += f"""
    "{patch['name'][:-4]}.*"
     {{
        type {boundaryConditions['pressureOutlet']['k_type']};
        value uniform {boundaryConditions['pressureOutlet']['k_value']};
    }}
    """
            else:
                pass 

    k_file += """
}"""
    return k_file

def create_omega_file(meshSettings,boundaryConditions):
    header = ampersandPrimitives.createFoamHeader(className="volScalarField", objectName="omega")
    dims = ampersandPrimitives.createDimensions(M=0,L=0,T=-1)
    internalField = ampersandPrimitives.createInternalFieldScalar(type="uniform", value=1.0e-6)
    omega_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
{"""
    # Loop through patches for each boundary condition
    for patch in meshSettings['patches']:
        #print(patch)
        omega_file += f"""
    {patch['name']}"""
        if(patch['type'] == 'patch' and patch['name'] == 'inlet'):
            omega_file += f"""
    {{
        type {boundaryConditions['velocityInlet']['omega_type']};
        value uniform {boundaryConditions['velocityInlet']['omega_value']};
    }}
    """
        if(patch['type'] == 'patch' and patch['name'] == 'outlet'):
            omega_file += f"""
    {{
        type {boundaryConditions['pressureOutlet']['omega_type']};
        value uniform {boundaryConditions['pressureOutlet']['omega_value']};
    }}
    """
        if(patch['type'] == 'wall'):
            omega_file += f"""
    {{
        type {boundaryConditions['wall']['omega_type']};
        value  {boundaryConditions['wall']['omega_value']};
    }}
    """
        if(patch['type'] == 'movingWall'):
            omega_file += f"""
    {{
        type {boundaryConditions['movingWall']['omega_type']};
        value  {boundaryConditions['movingWall']['omega_value']};
    }}
    """
    for patch in meshSettings['geometry']:
        if(patch['type'] == 'triSurfaceMesh'):
            if(patch['purpose'] == 'wall'):
                omega_file += f"""
    "{patch['name'][:-4]}.*"
    {{
        type {boundaryConditions['wall']['omega_type']};
        value  {boundaryConditions['wall']['omega_value']};
    }}
    """
            elif(patch['purpose'] == 'inlet'):
                k_file += f"""
    "{patch['name'][:-4]}.*"
    {{
        type {boundaryConditions['velocityInlet']['omega_type']};
        value uniform {boundaryConditions['velocityInlet']['omega_value']};
    }}
    """  
            elif(patch['purpose'] == 'outlet'):
                k_file += f"""
    "{patch['name'][:-4]}.*"
    {{
        type {boundaryConditions['pressureOutlet']['omega_type']};
        value uniform {boundaryConditions['pressureOutlet']['omega_value']};
    }}
    """
            else:
                pass 

    omega_file += """
}"""
    return omega_file

def create_epsilon_file(meshSettings,boundaryConditions):
    header = ampersandPrimitives.createFoamHeader(className="volScalarField", objectName="epsilon")
    dims = ampersandPrimitives.createDimensions(M=2,L=2,T=-3)
    internalField = ampersandPrimitives.createInternalFieldScalar(type="uniform", value=1.0e-6)
    epsilon_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
{"""
    # Loop through patches for each boundary condition
    for patch in meshSettings['patches']:
        #print(patch)
        epsilon_file += f"""
    {patch['name']}"""
        if(patch['type'] == 'patch' and patch['name'] == 'inlet'):
            epsilon_file += f"""
    {{
        type {boundaryConditions['velocityInlet']['epsilon_type']};
        value uniform {boundaryConditions['velocityInlet']['epsilon_value']};
    }}
    """
        if(patch['type'] == 'patch' and patch['name'] == 'outlet'):
            epsilon_file += f"""
    {{
        type {boundaryConditions['pressureOutlet']['epsilon_type']};
        value uniform {boundaryConditions['pressureOutlet']['epsilon_value']};
    }}
    """
        if(patch['type'] == 'wall'):
            epsilon_file += f"""
    {{
        type {boundaryConditions['wall']['epsilon_type']};
        value  {boundaryConditions['wall']['epsilon_value']};
    }}
    """
        if(patch['type'] == 'movingWall'):
            epsilon_file += f"""
    {{
        type {boundaryConditions['movingWall']['epsilon_type']};
        value  {boundaryConditions['movingWall']['epsilon_value']};
    }}
    """
    for patch in meshSettings['geometry']:
        if(patch['type'] == 'triSurfaceMesh'):
            if(patch['purpose'] == 'wall'):
                epsilon_file += f"""
    "{patch['name'][:-4]}.*"
    {{
        type {boundaryConditions['wall']['epsilon_type']};
        value  {boundaryConditions['wall']['epsilon_value']};
    }}
    """
            elif(patch['purpose'] == 'inlet'):
                k_file += f"""
    "{patch['name'][:-4]}.*"
    {{
        type {boundaryConditions['velocityInlet']['epsilon_type']};
        value uniform {boundaryConditions['velocityInlet']['epsilon_value']};
    }}
    """  
            elif(patch['purpose'] == 'outlet'):
                k_file += f"""
    "{patch['name'][:-4]}.*"
    {{
        type {boundaryConditions['pressureOutlet']['epsilon_type']};
        value uniform {boundaryConditions['pressureOutlet']['epsilon_value']};
    }}
    """
            else:
                pass 
        
    epsilon_file += """
}"""
    return epsilon_file

def create_nut_file(meshSettings,boundaryConditions):
    header = ampersandPrimitives.createFoamHeader(className="volScalarField", objectName="nut")
    dims = ampersandPrimitives.createDimensions(M=0,L=2,T=-1)
    internalField = ampersandPrimitives.createInternalFieldScalar(type="uniform", value=0)
    nut_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
{"""
    # Loop through patches for each boundary condition
    for patch in meshSettings['patches']:
        #print(patch)
        nut_file += f"""
    {patch['name']}"""
        if(patch['type'] == 'patch' and patch['name'] == 'inlet'):
            nut_file += f"""
    {{
        type {boundaryConditions['velocityInlet']['nut_type']};
        value uniform {boundaryConditions['velocityInlet']['nut_value']};
    }}
    """
        if(patch['type'] == 'patch' and patch['name'] == 'outlet'):
            nut_file += f"""
    {{
        type {boundaryConditions['pressureOutlet']['nut_type']};
        value uniform {boundaryConditions['pressureOutlet']['nut_value']};
    }}
    """
        if(patch['type'] == 'wall'):
            nut_file += f"""
    {{
        type {boundaryConditions['wall']['nut_type']};
        value  {boundaryConditions['wall']['nut_value']};
    }}
    """
        if(patch['type'] == 'movingWall'):
            nut_file += f"""
    {{
        type {boundaryConditions['movingWall']['nut_type']};
        value  {boundaryConditions['movingWall']['nut_value']};
    }}
    """
    for patch in meshSettings['geometry']:
        if(patch['type'] == 'triSurfaceMesh'):
            nut_file += f"""
    "{patch['name'][:-4]}.*"
    {{
        type {boundaryConditions['wall']['nut_type']};
        value  {boundaryConditions['wall']['nut_value']};
    }}
    """
    nut_file += """
}"""
    return nut_file

def update_boundary_conditions(boundaryConditions, inletValues):
    """
    Update boundary conditions with inlet values.

    Parameters:
    boundaryConditions (dict): Dictionary specifying boundary conditions for U, p, k, and omega.
    inletValues (dict): Dictionary specifying inlet values for U, p, k, and omega.
    """
    boundaryConditions['velocityInlet']['u_value'] = inletValues['U']
    boundaryConditions['velocityInlet']['p_value'] = inletValues['p']
    boundaryConditions['velocityInlet']['k_value'] = inletValues['k']
    boundaryConditions['velocityInlet']['omega_value'] = inletValues['omega']
    boundaryConditions['velocityInlet']['epsilon_value'] = inletValues['epsilon']
    boundaryConditions['velocityInlet']['nut_value'] = inletValues['nut']
    return boundaryConditions

def create_boundary_conditions(meshSettings, boundaryConditions):
    """
    Create boundary condition files for an OpenFOAM pimpleFoam simulation.

    Parameters:
    meshSettings (dict): Dictionary specifying mesh settings.
    boundaryConditions (dict): Dictionary specifying boundary conditions for U, p, k, and omega.
    inletValues (dict): Dictionary specifying inlet values for U, p, k, and omega.
    """
    u_file = create_u_file(meshSettings, boundaryConditions)
    p_file = create_p_file(meshSettings, boundaryConditions)
    k_file = create_k_file(meshSettings, boundaryConditions)
    omega_file = create_omega_file(meshSettings, boundaryConditions)
    epsilon_file = create_epsilon_file(meshSettings, boundaryConditions)
    nut_file = create_nut_file(meshSettings, boundaryConditions)
    #print(p_file)
    #print(u_file)
    print("Creating boundary conditions files")
    ampersandPrimitives.write_to_file("U", u_file)
   
    ampersandPrimitives.write_to_file("p", p_file)
    
    ampersandPrimitives.write_to_file("k", k_file)
   
    ampersandPrimitives.write_to_file("omega", omega_file)

    ampersandPrimitives.write_to_file("epsilon", epsilon_file)

    ampersandPrimitives.write_to_file("nut", nut_file)



if __name__ == '__main__':
    meshSettings = ampersandPrimitives.yaml_to_dict("meshSettings.yaml")
    create_boundary_conditions(meshSettings, boundaryConditions, inletValues)


   
