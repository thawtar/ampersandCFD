"""
-------------------------------------------------------------------------------
  ***    *     *  ******   *******  ******    *****     ***    *     *  ******   
 *   *   **   **  *     *  *        *     *  *     *   *   *   **    *  *     *  
*     *  * * * *  *     *  *        *     *  *        *     *  * *   *  *     *  
*******  *  *  *  ******   ****     ******    *****   *******  *  *  *  *     *  
*     *  *     *  *        *        *   *          *  *     *  *   * *  *     *  
*     *  *     *  *        *        *    *   *     *  *     *  *    **  *     *  
*     *  *     *  *        *******  *     *   *****   *     *  *     *  ******   
-------------------------------------------------------------------------------
 * AmpersandCFD is a minimalist streamlined OpenFOAM generation tool.
 * Copyright (c) 2024 THAW TAR
 * All rights reserved.
 *
 * This software is licensed under the GNU General Public License version 3 (GPL-3.0).
 * You may obtain a copy of the license at https://www.gnu.org/licenses/gpl-3.0.en.html
 */
"""

from typing import Any, Literal, Optional, Union, cast
from tkinter import filedialog, Tk

from ampersandCFD.models.inputs import FLUID_PYSICAL_PROPERTIES, FluidProperties, StlInput
from ampersandCFD.models.settings import BoundingBox, RefinementAmount, PatchProperty, PatchType
from ampersandCFD.utils.logger import logger

try:
    from PySide6.QtWidgets import QMessageBox
    from ampersandCFD.gui.dialogBoxes import inputDialogDriver, vectorInputDialogDriver
except:
    pass

ModificationType = Literal["Background Mesh", "Mesh Point", "Add Geometry", "Refinement Levels", "Boundary Conditions", "Fluid Properties", "Numerical Settings", "Simulation Control Settings", "Turbulence Model", "Post Processing Settings"]

class IOUtils:
    GUIMode: bool = False
    window: Any = None
    verbose: bool = False
    @staticmethod
    def print(*args):
        if IOUtils.GUIMode and IOUtils.window != None:
            IOUtils.window.updateTerminal(*args)
        elif IOUtils.verbose:
            logger.info(' '.join(map(str, args)))

    @staticmethod
    def warn(*args):
        if IOUtils.GUIMode:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Warning")
            msg.setInformativeText(*args)
            msg.setWindowTitle("Warning")
            msg.exec_()
        elif IOUtils.verbose:
            logger.warning(' '.join(map(str, args)))

    @staticmethod
    def error(*args):
        if IOUtils.GUIMode:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText(*args)
            msg.setWindowTitle("Error")
            msg.exec_()
        elif IOUtils.verbose:
            logger.error(' '.join(map(str, args)))

    @staticmethod
    def get_input(prompt):
        if IOUtils.GUIMode:
            input_str = inputDialogDriver(prompt)
            if (input_str == None):
                raise ValueError("User cancelled the operation")
            return input_str
        else:
            return input(prompt) 


    @staticmethod
    def get_input_int(prompt):
        if IOUtils.GUIMode:
            return int(inputDialogDriver(prompt, input_type="int"))
        else:
            try:
                return int(input(prompt))
            except:
                IOUtils.error(
                    "Invalid input. Please enter an integer.")
                return IOUtils.get_input_int(prompt)

    @staticmethod
    def get_input_float(prompt):
        if IOUtils.GUIMode:
            return float(inputDialogDriver(prompt, input_type="float"))
        else:
            try:
                return float(input(prompt))
            except:
                IOUtils.error("Invalid input. Please enter a number.")
                return IOUtils.get_input_float(prompt)

    @staticmethod
    def print_numbered_list(lst):
        for i in range(len(lst)):
            print(f"{i+1}. {lst[i]}")

    @staticmethod
    def get_input_vector(prompt):
        if IOUtils.GUIMode:
            return vectorInputDialogDriver(prompt)
        else:
            inp = input(prompt).split()
            try:
                vec = tuple(map(float, inp))
                if len(vec) != 3:
                    IOUtils.error("Invalid input. Please enter 3 numbers.")
                    # Recursively call the function until a valid input is given
                    return IOUtils.get_input_vector(prompt)
                return vec
            except:
                IOUtils.error("Invalid input. Please enter a list of numbers.")
                # Recursively call the function until a valid input is given
                return IOUtils.get_input_vector(prompt)

    @staticmethod
    def get_input_bool(prompt):
        try:
            return input(prompt).lower() in ['y', 'yes', 'true', '1']
        except:
            IOUtils.error(
                "Invalid input. Please enter a boolean value.")
            return IOUtils.get_input_bool(prompt)

    @staticmethod
    def get_option_choice(prompt, options, title=None):
        if title:
            IOUtils.print(title)
        IOUtils.print_numbered_list(options)
        choice = IOUtils.get_input_int(prompt)
        if choice > len(options) or choice <= 0:
            IOUtils.error(
                "Invalid choice. Please choose from the given options.")
            return IOUtils.get_option_choice(prompt, options)
        return choice-1


    @staticmethod
    def ask_for_directory(qt=False):
        try:
            if qt:
                from PySide6.QtWidgets import QFileDialog
                directory = QFileDialog.getExistingDirectory(
                    None, "Select Project Directory")
                return directory if directory else None
            else:
                root = Tk()
                root.withdraw()  # Hide the main window
                directory = filedialog.askdirectory(
                    title="Select Project Directory")
                return directory if directory else None
        except:
            return IOUtils.get_input("Select Project Directory: ")

    @staticmethod
    def get_file(filetypes=[("STL Geometry", "*.stl")], qt=False):
        try:
            if qt:
                from PySide6.QtWidgets import QFileDialog
                file = QFileDialog.getOpenFileName(
                    None, "Select File", filter="STL Geometry (*.stl)")
                return file[0] if file[0] else None
            else:
                root = Tk()
                root.withdraw()
                file = filedialog.askopenfilename(
                    title="Select File", filetypes=filetypes)
                return file if file else None
        except:
            return IOUtils.get_input("Select file: ")

    @staticmethod
    def show_title(title):
        total_len = 60
        half_len = (total_len - len(title))//2
        title = "-"*half_len + title + "-"*half_len
        IOUtils.print("\n" + title)

    @staticmethod
    def print_line():
        IOUtils.print("-"*60)


class AmpersandDataInput:
    @staticmethod
    def get_inlet_values():
        U = IOUtils.get_input_vector("Enter the velocity vector at the inlet (m/s): ")
        return U

    @staticmethod
    def choose_modification_type() -> ModificationType:
        options: list[Union[Literal['Mesh'], ModificationType]] = ['Mesh', 'Boundary Conditions', 'Fluid Properties', 'Numerical Settings',
                   'Simulation Control Settings', 'Turbulence Model', 'Post Processing Settings']
        current_modification = IOUtils.get_option_choice(prompt="Choose any option for project modification: ",
                                                             options=options, title="\nModify Project Settings")
        mesh_options: list[ModificationType] = ['Background Mesh', 'Mesh Point', 'Add Geometry', 'Refinement Levels']

        if current_modification < 0 or current_modification > len(options)-1:
            raise ValueError("Invalid option. Aborting operation")

        selected_modification = options[current_modification] 
        if selected_modification == "Mesh":
            return mesh_options[IOUtils.get_option_choice(prompt="Choose any option for mesh modification: ",
                                options=mesh_options, title="\nModify Mesh Settings")]
        else:
            return selected_modification


    @staticmethod
    def get_domain_size():
        IOUtils.print(
            "Domain size is the size of the computational domain in meters")
        minX, minY, minZ = IOUtils.get_input_vector("Xmin Ymin Zmin: ")
        maxX, maxY, maxZ = IOUtils.get_input_vector("Xmax Ymax Zmax: ")
        # check if the values are valid
        if (minX >= maxX or minY >= maxY or minZ >= maxZ):
            IOUtils.print(
                "Invalid domain size, please enter the values again")
            return AmpersandDataInput.get_domain_size()
        return BoundingBox(minx=minX, maxx=maxX, miny=minY, maxy=maxY, minz=minZ, maxz=maxZ)

    @staticmethod
    def get_cell_size():
        cellSize = IOUtils.get_input_float("Enter the maximum cell size (m): ")
        if (cellSize <= 0):
            IOUtils.print(
                "Invalid cell size, please enter the value again")
            AmpersandDataInput.get_cell_size()
        return cellSize


    @staticmethod
    def get_fluid_properties():
        rho = IOUtils.get_input_float(
            "Enter the density of the fluid (kg/m^3): ")
        nu = IOUtils.get_input_float(
            "Enter the kinematic viscosity of the fluid (m^2/s): ")
        if (rho <= 0 or nu <= 0):
            IOUtils.print("Invalid fluid properties, please enter the values again")
            AmpersandDataInput.get_fluid_properties()
        return FluidProperties(rho=rho, nu=nu)


    @staticmethod
    def get_turbulence_model():
        turbulence_models = ['kOmegaSST', 'kEpsilon', ]
        IOUtils.show_title("Turbulence models")
        for i in range(len(turbulence_models)):
            IOUtils.print(f"{i+1}. {turbulence_models[i]}")
        turbulence_model = IOUtils.get_input_int(
            "Choose the turbulence model: ")
        if turbulence_model > len(turbulence_models) or turbulence_model <= 0:
            IOUtils.error(
                "Invalid turbulence model. Defaulting to kOmegaSST.")
            turbulence_model = 1
        return turbulence_models[turbulence_model-1]

    @staticmethod
    def choose_fluid_properties():
        fluid_names = list(FLUID_PYSICAL_PROPERTIES.keys())
        IOUtils.print("Fluid properties")
        IOUtils.print("0. Enter fluid properties manually")
        for i in range(len(fluid_names)):
            IOUtils.print(f"{i+1}. {fluid_names[i]}")
        fluid_name = IOUtils.get_input_int("Choose the fluid properties:")

        if (fluid_name > len(FLUID_PYSICAL_PROPERTIES) or fluid_name <= 0):
            IOUtils.print("Please input fluid properties manually.")
            return AmpersandDataInput.get_fluid_properties()
        fluid = FLUID_PYSICAL_PROPERTIES[fluid_names[fluid_name-1]]
        return fluid

    @staticmethod
    def get_mesh_refinement_amount() -> RefinementAmount:
        ref_amounts = ["coarse", "medium", "fine"]
        ref_amount_index = IOUtils.get_input_int(
            "Enter the mesh refinement (0: coarse, 1: medium, 2: fine): ")
        if ref_amount_index not in [0, 1, 2]:
            IOUtils.print("Invalid mesh refinement level. Defaulting to medium.")
            ref_amount_index = 1
        return cast(RefinementAmount, ref_amounts[ref_amount_index])


    @staticmethod
    def get_patch_type() -> PatchType:
        purposes = ['wall', 'inlet', 'outlet', 'refinementRegion', 'refinementSurface',
                    'cellZone', 'baffles', 'symmetry', 'cyclic', 'empty',]
        IOUtils.print(f"Enter purpose for this STL geometry")
        IOUtils.print_numbered_list(purposes)
        purpose_no = IOUtils.get_input_int("Enter purpose number: ")-1
        if (purpose_no < 0 or purpose_no > len(purposes)-1):
            IOUtils.print(
                "Invalid purpose number. Setting purpose to wall")
            purpose = 'wall'
        else:
            purpose = purposes[purpose_no]
        return cast(PatchType, purpose)

    @staticmethod
    def get_patch_property(purpose: PatchType='wall') -> Optional[PatchProperty]:
        if purpose == 'inlet':
            U = AmpersandDataInput.get_inlet_values()
            return cast(PatchProperty, tuple(U))
        elif purpose == 'refinementRegion':
            refLevel = IOUtils.get_input_int("Enter refinement level: ")
            return refLevel
        elif purpose == 'cellZone':
            refLevel = IOUtils.get_input_int("Enter refinement level: ")
            createPatches = IOUtils.get_input_bool(
                "Create patches for this cellZone? (y/N): ")
            # 0 is just a placeholder for listing the patches
            return (refLevel, createPatches, 0)
        elif purpose == 'refinementSurface':
            refLevel = IOUtils.get_input_int("Enter refinement level: ")
            return refLevel



    @staticmethod
    def get_valid_stl_inputs() -> list[StlInput]:
        stl_inputs = []
        while True:
            stl_path = IOUtils.get_file([("STL Geometry", "*.stl"), ("OBJ Geometry", "*.obj")])
            if stl_path is None:
                break

            # Get purpose and properties 
            purpose = AmpersandDataInput.get_patch_type()
            property = None if IOUtils.GUIMode else AmpersandDataInput.get_patch_property(purpose)
            stl_inputs.append(StlInput(stl_path=stl_path, purpose=purpose, property=property))

            if not IOUtils.get_input_bool("Add another STL file (y/N)?: "):
                break

        return stl_inputs
