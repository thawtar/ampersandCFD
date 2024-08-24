from constants import meshSettings
from primitives import ampersandPrimitives

def generate_blockMeshDict(meshSettings):
    blockMeshDict = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}
 
// ********* Domain *********
scale {meshSettings['scale']};
 
vertices
(
    ({meshSettings['domain']['minx']} {meshSettings['domain']['miny']} {meshSettings['domain']['minz']})
    ({meshSettings['domain']['maxx']} {meshSettings['domain']['miny']} {meshSettings['domain']['minz']})
    ({meshSettings['domain']['maxx']} {meshSettings['domain']['maxy']} {meshSettings['domain']['minz']})
    ({meshSettings['domain']['minx']} {meshSettings['domain']['maxy']} {meshSettings['domain']['minz']})
    ({meshSettings['domain']['minx']} {meshSettings['domain']['miny']} {meshSettings['domain']['maxz']})
    ({meshSettings['domain']['maxx']} {meshSettings['domain']['miny']} {meshSettings['domain']['maxz']})
    ({meshSettings['domain']['maxx']} {meshSettings['domain']['maxy']} {meshSettings['domain']['maxz']})
    ({meshSettings['domain']['minx']} {meshSettings['domain']['maxy']} {meshSettings['domain']['maxz']})
);
 
blocks
(
    hex (0 1 2 3 4 5 6 7) ({meshSettings['domain']['nx']} {meshSettings['domain']['ny']} {meshSettings['domain']['nz']}) simpleGrading (1 1 1)
);
 
edges
(
);
 
boundary
(
"""
    for patch in meshSettings['patches']:
        blockMeshDict += f"""\n    {patch[list(patch.keys())[0]]}
    {{
        type {patch['type']};
        faces
        (
            ({patch['faces'][0]} {patch['faces'][1]} {patch['faces'][2]} {patch['faces'][3]})
        );
    }}\n"""
    
    blockMeshDict += """);
mergePatchPairs
(
);

// ************************************************************************* //
"""

    return blockMeshDict

# Generate blockMeshDict
# read in data to meshSettings from meshSettings.yaml
meshSettings = ampersandPrimitives.yaml_to_dict("meshSettings.yaml")
blockMeshDict = generate_blockMeshDict(meshSettings)

# Save to file
with open("blockMeshDict", "w") as f:
    f.write(blockMeshDict)


#print(blockMeshDict)

print("blockMeshDict file created.")
