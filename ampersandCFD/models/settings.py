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

from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Union, Optional, cast



Location = tuple[float, float, float]
RefinementAmount = Literal["coarse", "medium", "fine"]
class FluidProperties(BaseModel):
    rho: float
    nu: float


class BoundingBox(BaseModel):
    minx: float
    maxx: float
    miny: float
    maxy: float
    minz: float
    maxz: float

    def to_tuple(self):
        """
        Convert the object's bounding box coordinates to a tuple.

        Returns:
            list: A list containing the minimum and maximum coordinates 
                  of the bounding box in the following order:
                  [minx, maxx, miny, maxy, minz, maxz].
        """
        return [self.minx, self.maxx, self.miny, self.maxy, self.minz, self.maxz]

    def __repr__(self):
        return (
            f"Domain size:{'X':>10}{'Y':>10}{'Z':>10}\n"
            f"Min         {self.minx:>10.3f}{self.miny:>10.3f}{self.minz:>10.3f}\n"
            f"Max         {self.maxx:>10.3f}{self.maxy:>10.3f}{self.maxz:>10.3f}"
        )

    @property
    def size(self):
        """
        Get the size of the bounding box.

        Returns:
            tuple: A tuple containing the size of the bounding box in the following order:
                   (length, width, height).
        """
        return self.maxx - self.minx, self.maxy - self.miny, self.maxz - self.minz

    @property
    def max_length(self):
        """
        Get the maximum length of the bounding box.

        Returns:
            float: The maximum length of the bounding box.
        """
        return max(*self.size)

    @property
    def min_length(self):
        """
        Get the minimum length of the bounding box.

        Returns:
            float: The minimum length of the bounding box.
        """
        return min(*self.size)

    def scale_dimensions(self, xmin_offset: float = 0.0, xmax_offset: float = 0.0, ymin_offset: float = 0.0, ymax_offset: float = 0.0, zmin_offset: float = 0.0, zmax_offset: float = 0.0):

        return BoundingBox(
            minx = self.minx + xmin_offset,
            maxx = self.maxx + xmax_offset,
            miny = self.miny + ymin_offset,
            maxy = self.maxy + ymax_offset,
            minz = self.minz + zmin_offset,
            maxz = self.maxz + zmax_offset
        )

    @staticmethod
    def expand_domain(current: "BoundingBox", size: "BoundingBox"):
        """
        Update the bounding box coordinates with the given size.
        """
        return BoundingBox(
            minx=min(size.minx, current.minx),
            maxx=max(size.maxx, current.maxx),
            miny=min(size.miny, current.miny),
            maxy=max(size.maxy, current.maxy),
            minz=min(size.minz, current.minz),
            maxz=max(size.maxz, current.maxz),
        )




class Domain(BoundingBox):
    minx: float = 0
    maxx: float = 0
    miny: float = 0
    maxy: float = 0
    minz: float = 0
    maxz: float = 0
    nx: int = 0
    ny: int = 0
    nz: int = 0

    def __repr__(self):
        return (
            super().__repr__() + "\n"
            f"Background mesh size: {self.nx}x{self.ny}x{self.nz} cells\n"
        )

    @staticmethod
    def from_bbox(bbox: BoundingBox, nx: int = 0, ny: int = 0, nz: int = 0):
        return Domain(
            minx=bbox.minx,
            maxx=bbox.maxx,
            miny=bbox.miny,
            maxy=bbox.maxy,
            minz=bbox.minz,
            maxz=bbox.maxz,
            nx=nx,
            ny=ny,
            nz=nz,
        )

    @property
    def bbox(self):
        return BoundingBox(
            minx=self.minx,
            maxx=self.maxx,
            miny=self.miny,
            maxy=self.maxy,
            minz=self.minz,
            maxz=self.maxz
        )


    @staticmethod
    def expand_domain(current: "Domain", new_domain: Union[BoundingBox, "Domain"]):
        """
        Update the bounding box coordinates with the given domain size.
        """
        if not isinstance(new_domain, Domain):
            new_domain = Domain.from_bbox(new_domain)

        return Domain(
            minx=min(new_domain.minx, current.minx),
            maxx=max(new_domain.maxx, current.maxx),
            miny=min(new_domain.miny, current.miny),
            maxy=max(new_domain.maxy, current.maxy),
            minz=min(new_domain.minz, current.minz),
            maxz=max(new_domain.maxz, current.maxz),
            nx=max(new_domain.nx if (isinstance(new_domain, Domain)) else 0, current.nx),
            ny=max(new_domain.ny if (isinstance(new_domain, Domain)) else 0, current.ny),
            nz=max(new_domain.nz if (isinstance(new_domain, Domain)) else 0, current.nz)
        )


    @staticmethod
    def update_size(current: "Domain", new_bbox: BoundingBox):
        return Domain.from_bbox(new_bbox, nx=current.nx, ny=current.ny, nz=current.nz)



Number = Union[int, float]

BCType = Literal[
    "patch",  # generic patch
    "symmetry",  # plane of symmetry
    "symmetryPlane",  # plane of symmetry
    "empty",  # front and back planes of a 2D geometry
    "wedge",  # wedge front and back for an axi-symmetric geometry
    "cyclic",  # cyclic plane
    "wall",  # wall — used for wall functions in turbulent flows
    "processor"  # inter-processor boundary
]

PatchType = Literal['inlet', 'outlet', 'symmetry', 'wall', 'searchableBox', 'refinementSurface', 'refinementRegion', 'cellZone', 'baffles', 'symmetry','cyclic','empty', "movingWall"]
PatchProperty = Union[tuple[Number, Number, Number], Number]
class Patch(BaseModel):
    type: PatchType
    property: Optional[PatchProperty] = None
    

class BCPatch(Patch):
    bcType: Optional[BCType] = None
    faces: List[int]
    
class TriSurfaceMeshGeometry(Patch):
    refineMin: int
    refineMax: int
    featureEdges: bool
    featureLevel: int
    nLayers: int
    bounds: BoundingBox

class SearchableBoxGeometry(Patch):
    type: Literal["searchableBox"] = "searchableBox"
    bbox: BoundingBox
    refineMax: int


Geometry = Union[TriSurfaceMeshGeometry, SearchableBoxGeometry]

class SnappyHexSteps(BaseModel):
    castellatedMesh: str = 'true'
    snap: str = 'true'
    addLayers: str = 'true'


class CastellatedMeshControls(BaseModel):
    maxLocalCells: int = 10_000_000
    maxGlobalCells: int = 50_000_000
    minRefinementCells: int = 10
    maxLoadUnbalance: float = 0.10
    nCellsBetweenLevels: int = 5
    features: List = []
    refinementSurfaces: List = []
    resolveFeatureAngle: int = 25
    refinementRegions: List = []
    locationInMesh: Location = (0, 0, 0)
    allowFreeStandingZoneFaces: str = 'false'


class SnapControls(BaseModel):
    nSmoothPatch: int = 3
    tolerance: float = 2.0
    nSolveIter: int = 50
    nRelaxIter: int = 5
    nFeatureSnapIter: int = 10
    implicitFeatureSnap: str = 'false'
    explicitFeatureSnap: str = 'true'
    multiRegionFeatureSnap: str = 'false'


class AddLayersControls(BaseModel):
    relativeSizes: str = 'true'
    expansionRatio: float = 1.4
    finalLayerThickness: float = 0.3
    firstLayerThickness: float = 0.001
    minThickness: float = 1e-7
    nGrow: int = 0
    featureAngle: int = 180
    slipFeatureAngle: int = 30
    nRelaxIter: int = 3
    nSmoothSurfaceNormals: int = 1
    nSmoothNormals: int = 3
    nSmoothThickness: int = 10
    maxFaceThicknessRatio: float = 0.5
    maxThicknessToMedialRatio: float = 0.3
    minMedianAxisAngle: int = 90
    nBufferCellsNoExtrude: int = 0
    nLayerIter: int = 50


class MeshQualityControls(BaseModel):
    maxNonOrtho: int = 70
    maxBoundarySkewness: int = 4
    maxInternalSkewness: int = 4
    maxConcave: int = 80
    minTetQuality: float = 1.0e-30
    minVol: float = 1e-30
    minArea: float = 1e-30
    minTwist: float = 0.001
    minDeterminant: float = 0.001
    minFaceWeight: float = 0.001
    minVolRatio: float = 0.001
    minTriangleTwist: int = -1
    nSmoothScale: int = 4
    errorReduction: float = 0.75

class MeshSettings(BaseModel):
    domain: Domain = Domain()
    scale: float = 1.0
    maxCellSize: float = 0.5
    refAmount: RefinementAmount = "coarse"

    onGround: bool = False
    halfModel: bool = False
    internalFlow: bool = False

    patches: dict[str, BCPatch] = {
        'inlet': BCPatch(type='inlet', bcType="patch",property=(1, 0, 0), faces=[0, 4, 7, 3]),
        'outlet': BCPatch(type='outlet', bcType="patch", faces=[1, 5, 6, 2]),
        'front': BCPatch(type='symmetry', bcType="symmetry", faces=[0, 1, 5, 4]),
        'back': BCPatch(type='symmetry', bcType="symmetry", faces=[2, 3, 7, 6]),
        'bottom': BCPatch(type='symmetry', bcType="symmetry", faces=[0, 1, 2, 3]),
        'top': BCPatch(type='symmetry', bcType="symmetry", faces=[4, 5, 6, 7]),
    }
    geometry: dict[str, Geometry] = {}

    @property
    def triSurfaceMeshGeometry(self):
        return {k: v for k, v in self.geometry.items() if isinstance(v, TriSurfaceMeshGeometry)}

class SnappyHexMeshSettings(MeshSettings):
    snappyHexSteps: SnappyHexSteps = SnappyHexSteps()
    castellatedMeshControls: CastellatedMeshControls = CastellatedMeshControls()
    snapControls: SnapControls = SnapControls()
    addLayersControls: AddLayersControls = AddLayersControls()
    meshQualityControls: MeshQualityControls = MeshQualityControls()
    mergeTolerance: float = 1e-6
    debug: int = 0


class PhysicalProperties(BaseModel):
    fluid: FluidProperties = Field(default_factory=lambda: FluidProperties(rho=1.0, nu=1.0e-6))
    g: List[float] = [0, 0, -9.81]
    pRef: int = 0
    Cp: int = 1000
    thermo: str = 'hPolynomial'
    Pr: float = 0.7
    TRef: int = 300
    turbulenceModel: str = 'kOmegaSST'

    @property
    def nu(self):
        return self.fluid.nu
    
    @property
    def rho(self):
        return self.fluid.rho


class DdtSchemes(BaseModel):
    default: str = 'steadyState'


class GradSchemes(BaseModel):
    default: str = 'Gauss linear'
    grad_p: str = 'Gauss linear'
    grad_U: str = 'cellLimited Gauss linear 1'


class DivSchemes(BaseModel):
    default: str = 'Gauss linear'
    div_phi_U: str = 'Gauss linearUpwind grad(U)'
    div_phi_k: str = 'Gauss upwind'
    div_phi_omega: str = 'Gauss upwind'
    div_phi_epsilon: str = 'Gauss upwind'
    div_phi_nut: str = 'Gauss upwind'
    div_nuEff_dev_T_grad_U: str = 'Gauss linear'


class LaplacianSchemes(BaseModel):
    default: str = 'Gauss linear limited 0.667'


class InterpolationSchemes(BaseModel):
    default: str = 'linear'


class SnGradSchemes(BaseModel):
    default: str = 'limited 0.667'


class FluxRequired(BaseModel):
    default: str = 'no'


class PimpleDictResidualControl(BaseModel):
    p: float = 1e-3
    U: float = 1e-3
    k: float = 1e-3
    omega: float = 1e-3
    epsilon: float = 1e-3
    nut: float = 1e-3


class PimpleDict(BaseModel):
    nOuterCorrectors: int = 20
    nCorrectors: int = 1
    nNonOrthogonalCorrectors: int = 1
    pRefCell: int = 0
    pRefValue: int = 0
    residualControl: PimpleDictResidualControl = PimpleDictResidualControl()


class RelaxationFactors(BaseModel):
    U: float = 0.9
    k: float = 0.7
    omega: float = 0.7
    epsilon: float = 0.7
    nut: float = 0.7
    p: float = 1.0


class SimpleDictResidualControl(BaseModel):
    U: float = 1e-4
    p: float = 1e-4
    k: float = 1e-4
    omega: float = 1e-4
    epsilon: float = 1e-4
    nut: float = 1e-4


class SimpleDict(BaseModel):
    nNonOrthogonalCorrectors: int = 2
    consistent: str = 'true'
    residualControl: SimpleDictResidualControl = SimpleDictResidualControl()


class PotentialFlowDict(BaseModel):
    nonOrthogonalCorrectors: int = 10


class NumericalSettings(BaseModel):
    ddtSchemes: DdtSchemes = DdtSchemes()
    gradSchemes: GradSchemes = GradSchemes()
    divSchemes: DivSchemes = DivSchemes()
    laplacianSchemes: LaplacianSchemes = LaplacianSchemes()
    interpolationSchemes: InterpolationSchemes = InterpolationSchemes()
    snGradSchemes: SnGradSchemes = SnGradSchemes()
    fluxRequired: FluxRequired = FluxRequired()
    wallDist: str = 'meshWave'
    pimpleDict: PimpleDict = PimpleDict()
    relaxationFactors: RelaxationFactors = RelaxationFactors()
    simpleDict: SimpleDict = SimpleDict()
    potentialFlowDict: PotentialFlowDict = PotentialFlowDict()


class SolverSettings(BaseModel):
    U: Dict[str, Union[str, float, int]] = {
        'type': 'smoothSolver',
        'smoother': 'GaussSeidel',
        'tolerance': 1e-08,
        'relTol': 0.1,
    }
    p: Dict[str, Union[str, float, int]] = {
        'type': 'GAMG',
        'smoother': 'GaussSeidel',
        'tolerance': 1e-07,
        'relTol': 0.01,
        'maxIter': 100,
        'agglomerator': 'faceAreaPair',
        'nCellsInCoarsestLevel': 10,
        'mergeLevels': 1,
        'cacheAgglomeration': 'true',
        'nSweeps': 1,
        'nPreSweeps': 0,
        'nPostSweeps': 0,
    }
    k: Dict[str, Union[str, float, int]] = {
        'type': 'smoothSolver',
        'smoother': 'GaussSeidel',
        'tolerance': 1e-08,
        'relTol': 0.1,
    }
    omega: Dict[str, Union[str, float, int]] = {
        'type': 'smoothSolver',
        'smoother': 'GaussSeidel',
        'tolerance': 1e-08,
        'relTol': 0.1,
    }
    epsilon: Dict[str, Union[str, float, int]] = {
        'type': 'smoothSolver',
        'smoother': 'GaussSeidel',
        'tolerance': 1e-08,
        'relTol': 0.1,
    }
    nut: Dict[str, Union[str, float, int]] = {
        'type': 'smoothSolver',
        'smoother': 'GaussSeidel',
        'tolerance': 1e-08,
        'relTol': 0.1,
    }
    Phi: Dict[str, Union[str, float, int]] = {
        'type': 'GAMG',
        'smoother': 'GaussSeidel',
        'tolerance': 1e-08,
        'relTol': 0.01,
        'maxIter': 100,
        'agglomerator': 'faceAreaPair',
        'nCellsInCoarsestLevel': 10,
        'mergeLevels': 1,
        'cacheAgglomeration': 'true',
        'nSweeps': 1,
        'nPreSweeps': 0,
        'nPostSweeps': 0,
    }


class BoundaryCondition(BaseModel):
    u_type: str
    u_value: tuple[float, float, float]
    p_type: Literal['fixedValue', 'zeroGradient', 'totalPressure']
    p_value: Union[float, str]
    k_type: Literal['fixedValue', 'zeroGradient', 'kqRWallFunction']
    k_value: Union[float, str]
    omega_type: Literal['fixedValue', 'zeroGradient', 'omegaWallFunction']
    omega_value: Union[float, str]
    epsilon_type: Literal['fixedValue', 'zeroGradient', 'epsilonWallFunction']
    epsilon_value: Union[float, str]
    nut_type: Literal['calculated', 'nutkWallFunction']
    nut_value: Union[int, str]

    @property
    def u_max(self):
        """
        Get the maximum velocity value in the boundary condition.
        """
        return max(self.u_value)

class BoundaryConditions(BaseModel):
    velocityInlet: BoundaryCondition = BoundaryCondition(
        u_type='fixedValue', u_value=(1, 0, 0),
        p_type='zeroGradient', p_value=0,
        k_type='fixedValue', k_value=0.1,
        omega_type='fixedValue', omega_value=1,
        epsilon_type='fixedValue', epsilon_value=0.1,
        nut_type='calculated', nut_value=0
    )
    pressureOutlet: BoundaryCondition = BoundaryCondition(
        u_type='inletOutlet', u_value=(0, 0, 0),
        p_type='fixedValue', p_value=0,
        k_type='zeroGradient', k_value=1.0e-6,
        omega_type='zeroGradient', omega_value=1.0e-6,
        epsilon_type='zeroGradient', epsilon_value=1.0e-6,
        nut_type='calculated', nut_value=0
    )
    wall: BoundaryCondition = BoundaryCondition(
        u_type='fixedValue', u_value=(0, 0, 0),
        p_type='zeroGradient', p_value=0,
        k_type='kqRWallFunction', k_value='$internalField',
        omega_type='omegaWallFunction', omega_value='$internalField',
        epsilon_type='epsilonWallFunction', epsilon_value='$internalField',
        nut_type='nutkWallFunction', nut_value='$internalField'
    )
    movingWall: BoundaryCondition = BoundaryCondition(
        u_type='movingWallVelocity', u_value=(0, 0, 0),
        p_type='zeroGradient', p_value=0,
        k_type='kqRWallFunction', k_value='$internalField',
        omega_type='omegaWallFunction', omega_value='$internalField',
        epsilon_type='epsilonWallFunction', epsilon_value='$internalField',
        nut_type='nutkWallFunction', nut_value='$internalField'
    )


class ControlSettings(BaseModel):
    transient: bool = False
    potentialFoam: bool = True
    application: str = 'simpleFoam'
    startTime: int = 0
    endTime: int = 1000
    deltaT: int = 1
    startFrom: str = 'startTime'
    stopAt: str = 'endTime'
    writeControl: str = 'runTime'
    writeInterval: int = 100
    purgeWrite: int = 0
    writeFormat: str = 'binary'
    writePrecision: int = 6
    writeCompression: str = 'off'
    timeFormat: str = 'general'
    timePrecision: int = 6
    runTimeModifiable: str = 'true'
    adjustTimeStep: str = 'no'
    maxCo: float = 0.5
    functions: List = []
    libs: List = []
    allowSystemOperations: str = 'true'
    runTimeControl: str = 'adjustableRunTime'


class ParallelSettings(BaseModel):
    numberOfSubdomains: int = 4
    method: str = 'scotch'


class PostProcessSettings(BaseModel):
    FOs: bool = True
    minMax: bool = True
    massFlow: bool = True
    yPlus: bool = True
    forces: bool = True
    probeLocations: set[Location] = Field(default_factory=set)


class TransientInput(BaseModel):
    end_time: int
    time_step: int
    write_interval: int


class SimulationSettings(BaseModel):
    mesh: SnappyHexMeshSettings = SnappyHexMeshSettings()
    physicalProperties: PhysicalProperties = PhysicalProperties()
    numerical: NumericalSettings = NumericalSettings()
    solver: SolverSettings = SolverSettings()
    boundaryConditions: BoundaryConditions = BoundaryConditions()
    control: ControlSettings = ControlSettings()
    parallel: Optional[ParallelSettings] = ParallelSettings()
    postProcess: PostProcessSettings = PostProcessSettings()

    def set_half_model(self, is_half_model: bool):
        self.mesh.halfModel = is_half_model
        if is_half_model:
            self.mesh.patches['back'].type = 'symmetry'

    def set_inlet_values(self, U: Optional[tuple[float, float, float]] = None):
        if (not self.mesh.internalFlow):  # external flow
            assert U is not None, "Inlet velocity is not set, required for external flow"
            self.boundaryConditions.velocityInlet.u_value = U
        else:  # internal flow
            # Use inlet values from the stl file
            # TODO: check this out and ensure it sets once
            for geometry in self.mesh.geometry.values():
                if isinstance(geometry, TriSurfaceMeshGeometry) and geometry.type == 'inlet':
                    U_stl = cast(tuple[float, float, float], geometry.property or U)
                    self.boundaryConditions.velocityInlet.u_value = U_stl

    def set_transient_settings(self, transient: Union[TransientInput, Literal[False]]):
        self.control.transient = isinstance(transient, TransientInput)
        if isinstance(transient, TransientInput):
            self.control.application = 'pimpleFoam'
            self.control.endTime = transient.end_time
            self.control.writeInterval = transient.write_interval
            self.control.deltaT = transient.time_step
            self.control.adjustTimeStep = 'no'
            self.control.maxCo = 0.9
            self.numerical.ddtSchemes.default = 'Euler'
            # if steady state, SIMPLEC is used. If transient, PIMPLE is used
            # for PIMPLE, the relaxation factors are set to 0.7 and p = 0.3
            self.numerical.relaxationFactors.p = 0.3


    def set_post_process_settings(self, useFOs: bool):
        self.postProcess.FOs = useFOs
        meshPoint = self.mesh.castellatedMeshControls.locationInMesh
        self.postProcess.massFlow = useFOs
        self.postProcess.minMax = useFOs
        self.postProcess.yPlus = useFOs
        self.postProcess.forces = useFOs
        self.postProcess.probeLocations.add(meshPoint)

