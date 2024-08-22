import yaml

# this function reads a yaml file and returns a dictionary
def read_yaml_file(yaml_file):
    with open(yaml_file, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data

# this is an example yaml file for blockMeshDict and snappyHexMeshDict

# blockMeshDict: 

# vertices:
# - 0 0 0
# - 1 0 0
# - 1 1 0
# - 0 1 0
# - 0 0 1
# - 1 0 1
# - 1 1 1
# - 0 1 1
# blocks:
# - hex (0 1 2 3 4 5 6 7) (10 10 10) simpleGrading (1 1 1)
# edges:
# - arc 0 1 (0 0 1)
# - arc 1 2 (1 0 0)
# - arc 2 3 (0 1 0)
# - arc 3 0 (0 0 -1)
# - arc 4 5 (0 1 0)
# - arc 5 6 (0 0 1)
# - arc 6 7 (1 0 0)
# - arc 7 4 (0 -1 0)
# boundary:
# - name: front
#   faces:
#   - (0 1 2 3)
# - name: back
#   faces:
#   - (4 5 6 7)
# - name: right
#   faces:
#   - (1 5 6 2)
# - name: left
#   faces:
#   - (0 4 7 3)
# - name: top
#   faces:
#   - (3 2 6 7)
# - name: bottom
#   faces:
#   - (0 1 5 4)

# snappyHexMeshDict file in yaml format

# castellatedMeshControls:
#   maxLocalCells: 1000000
#   maxGlobalCells: 2000000
#   minRefinementCells: 0
#   nCellsBetweenLevels: 1
#   features:
#     - file.stl
#     - {
#         file: file.stl
#         level: 2
#       }
#     - {
#         file: file.stl
#         level: 3
#       }
#     - {
#         file: file.stl
#         level: 4
#       }
#     - {
#         file: file.stl
#         level: 5
#       }

# snapControls:
#   nSmoothPatch: 3
#   tolerance: 2.0
#   nSolveIter: 30
#   nRelaxIter: 5

# addLayersControls:
#   relativeSizes: true
#   layers:
#     - {
#         name: layer1
#         nSurfaceLayers: 1
#       }
#     - {
#         name: layer2
#         nSurfaceLayers: 2
#       }

# meshQualityControls:
#   nSmoothScale: 4
#   errorReduction: 0.75

# writeFlags:
#   - default




def create_yaml_file(blockMeshDict_file, snappyHexMeshDict_file, output_yaml_file):
    # Read blockMeshDict file
    with open(blockMeshDict_file, 'r') as blockMeshDict:
        blockMeshDict_data = blockMeshDict.read()

    # Read snappyHexMeshDict file
    with open(snappyHexMeshDict_file, 'r') as snappyHexMeshDict:
        snappyHexMeshDict_data = snappyHexMeshDict.read()

    # Create YAML data from blockMeshDict and snappyHexMeshDict data
    yaml_data = {
        'blockMeshDict': blockMeshDict_data,
        'snappyHexMeshDict': snappyHexMeshDict_data
    }

    # Write YAML data to output file
    with open(output_yaml_file, 'w') as output_file:
        yaml.dump(yaml_data, output_file)

# Example usage
blockMeshDict_file = '/path/to/blockMeshDict'
snappyHexMeshDict_file = '/path/to/snappyHexMeshDict'
output_yaml_file = '/path/to/output.yaml'



create_yaml_file(blockMeshDict_file, snappyHexMeshDict_file, output_yaml_file)

