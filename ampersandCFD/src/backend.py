# backend module for the ampersandCFD project
# Description: This file contains the code to generate OpenFOAM files

import os
import yaml
from primitives import ampersandPrimitives
from constants import meshSettings
#from ../constants/constants import meshSettings


class ampersandEngine: # ampersandEngine class to handle the generation of OpenFOAM files
    # this class will contain the methods to handle the logic and program flow
    def __init__(self):
        pass
  

if __name__ == '__main__':
    # Specify the output YAML file
    output_file = 'meshSettings.yaml'

    # Convert the dictionary to a YAML file
    ampersandPrimitives.dict_to_yaml(meshSettings, output_file)

    dict_ = ampersandPrimitives.yaml_to_dict(output_file)
    print(dict_)

