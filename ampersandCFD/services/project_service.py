from pathlib import Path
import shutil
from typing import Optional, Union

import yaml
from ampersandCFD.generators.blockMeshDict import BlockMeshDictGenerator
from ampersandCFD.generators.boundaryConditionDict import BoundaryConditionDictGenerator
from ampersandCFD.generators.controlDict import ControlDictGenerator
from ampersandCFD.generators.decomposeParDict import DecomposeParDictGenerator
from ampersandCFD.generators.fvDict import FVDictGenerator
from ampersandCFD.models.inputs import CreateProjectInput, PathLike, StlInput
from ampersandCFD.models.settings import SimulationSettings
from ampersandCFD.generators.postProcessDict import PostProcessGenerator
from ampersandCFD.utils.io import IOUtils
from ampersandCFD.models.project import AmpersandProject
from ampersandCFD.generators.cmdScript import CmdScriptGenerator
from ampersandCFD.generators.snappyHexMeshDict import SnappyHexMeshDictGenerator
from ampersandCFD.generators.surfaceExtractorDict import SurfaceExtractorDictGenerator
from ampersandCFD.generators.constantDict import ConstantDictGenerator
from ampersandCFD.utils.stl_analysis import StlAnalysis


# Custom representers for sets and tuples
def represent_set(dumper, data):
    return dumper.represent_list(sorted(data))  # Convert set to sorted list for YAML

def represent_tuple(dumper, data):
    return dumper.represent_list(data)  # Convert tuple to list for YAML

# Register custom representers
yaml.add_representer(set, represent_set)
yaml.add_representer(tuple, represent_tuple)

class ProjectService:
    @staticmethod
    def create_project(project_path: PathLike, input: Optional[CreateProjectInput] = None):
        """Create the project directory structure for an OpenFOAM case.
        
        Args:
            project_path: Path where the project should be created, can be string or Path

        Raises:
            ValueError: If project_path is None
            OSError: If there are issues creating directories or changing directory
        """
        IOUtils.print("Creating the project")

        if project_path is None:
            raise ValueError("No project path provided")


        settings = SimulationSettings()
        if (input):
            settings.mesh.refAmount = input.refinement_amount
            settings.mesh.internalFlow = input.is_internal_flow
            settings.mesh.onGround = input.on_ground or False
            settings.physicalProperties.fluid = input.fluid

            if settings.parallel and input.n_core > 1:
                settings.parallel.numberOfSubdomains = input.n_core
            else:
                settings.parallel = None

            settings.set_transient_settings(input.transient)
            settings.set_half_model(input.is_half_model)

            project = AmpersandProject(project_path, settings)


            for stl_file in input.stl_files:
                ProjectService.add_stl_file(project, stl_file)

            settings.set_inlet_values(input.inlet_values)
            settings.set_post_process_settings(input.use_function_objects)

        ProjectService.write_project(project)

        return project

    @staticmethod
    def load_project(project_path: PathLike):
        IOUtils.print(f"Loading project from path: {project_path}")
        with Path(project_path, "project_settings.yaml").open() as f:
            settings = SimulationSettings.model_validate(yaml.safe_load(f))
        project = AmpersandProject(project_path, settings)

        ProjectService.validate_project(project)

        IOUtils.print("Project loaded successfully")
        return project

    @staticmethod
    def write_project(project: AmpersandProject):
        # Create required OpenFOAM directories 
        required_dirs = [
            project.project_path / "0",
            project.project_path / "constant",
            project.project_path / "system",
            project.project_path / "constant" / "triSurface"
        ]

        try:
            for directory in required_dirs:
                if not directory.exists():
                    directory.mkdir(parents=True)
                    IOUtils.print(f"Created {directory} directory")
        except OSError as e:
            raise OSError(f"Failed to create OpenFOAM directory structure: {e}")
        
        ProjectService.write_openfoam_files(project)
        ProjectService.write_settings(project)

    @staticmethod
    def write_settings(project: AmpersandProject):
        IOUtils.print("Writing settings to project_settings.yaml")
        Path(project.project_path / "project_settings.yaml").write_text(
            yaml.dump(project.settings.model_dump(), default_flow_style=False, sort_keys=False)
        )


 
    @staticmethod
    def add_stl_file(project: AmpersandProject, stl_file: StlInput):
        # Convert paths to Path objects
        stl_path = Path(stl_file.stl_path)

        # Validate input file
        if not stl_path.exists():
            raise FileNotFoundError(f"STL file {stl_path} does not exist")
            
        StlAnalysis.add_stl_to_settings(project.settings, stl_path, stl_file.purpose, stl_file.property)

        # Copy STL file to project
        dest_path = Path(project.project_path) / "constant" / "triSurface" / stl_path.name
        # if dest_path.exists():
        #     raise ValueError(f"STL file {stl_path.name} already exists in project")

        try:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(stl_path, dest_path)
            IOUtils.print(f"Copied {dest_path.name} to {dest_path}")
        except OSError as e:
            raise RuntimeError(f"Failed to copy STL file: {e}")

        # Set solid name in STL file
        try:
            StlAnalysis.set_stl_solid_name(dest_path)
        except Exception as e:
            raise RuntimeError(f"Failed to set STL solid name: {e}")

        return dest_path


    @staticmethod
    def write_openfoam_files(project: AmpersandProject):
        if (not project.project_path.exists()):
            raise FileNotFoundError(f"Project not found at: {project.project_path}")
        project_path = project.project_path
        BoundaryConditionDictGenerator.write(project.settings.mesh, project.settings.boundaryConditions, project_path)

        # go inside the constant directory
        IOUtils.print("Creating constant properties")
        ConstantDictGenerator.write(project.settings.physicalProperties, project_path)

        # create the controlDict file
        IOUtils.print("Creating the system files")
        ControlDictGenerator.write(project.settings.control, project_path)
        BlockMeshDictGenerator.write(project.settings.mesh, project_path)
        SnappyHexMeshDictGenerator.write(project.settings.mesh, project_path)
        
        
        SurfaceExtractorDictGenerator.write(project.settings.mesh, "surfaceFeatureExtractDict", project_path)
        FVDictGenerator.write(project.settings.numerical, project.settings.solver, project_path)
        if project.settings.parallel:
            DecomposeParDictGenerator.write(project.settings.parallel, project_path)
        PostProcessGenerator.write(project.settings.mesh, project.settings.postProcess, project_path)
        CmdScriptGenerator.write(project.settings, project_path)

        IOUtils.print("\n-----------------------------------")
        IOUtils.print("Project files created successfully!")
        IOUtils.print("-----------------------------------\n")



    @staticmethod
    def validate_project(project: Union[AmpersandProject, str, Path]):
        project_path = Path(project) if isinstance(project, (str, Path)) else project.project_path
        ProjectService.check_directory(project_path / "0", project_path / "0.orig", copy=True)
        ProjectService.check_directory(project_path / "constant")
        ProjectService.check_directory(project_path / "system")
        ProjectService.check_directory(project_path / "constant/triSurface", check_files=True)



    @staticmethod
    def check_directory(path: Union[Path, str], fallback=None, copy=False, check_files=False):
        path = Path(path)
        if not path.exists():
            if fallback and Path(fallback).exists() and copy:
                IOUtils.print(f"{fallback} directory found. Copying to {path}")
                shutil.copytree(fallback, path)
            else:
                raise FileNotFoundError(f"{path} directory not found.")
        if check_files:
            if not list(path.iterdir()):
                raise FileNotFoundError(f"No files found in {path}.")

    @staticmethod
    def check_log_files(project_path: PathLike):
        project_path = Path(project_path)
        log_files = list(project_path.iterdir())
        if 'log.simpleFoam' in [f.name for f in log_files] or 'log.pimpleFoam' in [f.name for f in log_files]:
            IOUtils.print("Simulation log file found")
            return True
        IOUtils.print("No simulation log files found.")
        return False

    @staticmethod
    def check_post_process_files(project_path: PathLike):
        project_path = Path(project_path)
        post_process_path = project_path / "postProcessing/probe/0"
        if not post_process_path.exists():
            IOUtils.print(f"{post_process_path} directory does not exist.")
            return False
        files = [f.name for f in post_process_path.iterdir()]
        if 'U' not in files or 'p' not in files:
            IOUtils.print("Required files 'U' and 'p' not found in postProcessing.")
            return False
        return True

    @staticmethod
    def check_forces_files(project_path: PathLike):
        project_path = Path(project_path)
        forces_path = project_path / "postProcessing/forces/0"
        if not forces_path.exists():
            IOUtils.print(f"{forces_path} directory does not exist.")
            return False
        files = [f.name for f in forces_path.iterdir()]
        if 'force.dat' not in files:
            IOUtils.print("force.dat file not found in forces directory.")
            return False
        return True
