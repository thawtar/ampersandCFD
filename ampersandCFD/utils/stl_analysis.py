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

import os
from pathlib import Path
from typing import Union
from pydantic import BaseModel
import vtk
import numpy as np
import math
from ampersandCFD.models.settings import BoundingBox, Domain, MeshSettings, SearchableBoxGeometry, SimulationSettings, TriSurfaceMeshGeometry, RefinementAmount, PatchType, PatchProperty
from ampersandCFD.thirdparty.stlToOpenFOAM import find_inside_point, is_point_inside, read_stl_file
from ampersandCFD.thirdparty.stlToOpenFOAM import extract_curvature_data, compute_curvature
from ampersandCFD.utils.io import IOUtils
from ampersandCFD.utils.turbulence import TurbulenceUtils

class BoundaryLayer(BaseModel):
    yPlus: float
    y: float
    first_layer_thickness: float
    final_layer_thickness: float
    nLayers: int


class StlAnalysis:
    @staticmethod
    def calc_domain_bbox(stl_bbox: BoundingBox, size_factor=1.0, on_ground=False, internal_flow=False, is_half_model=False):
        characteristic_length = stl_bbox.max_length

        characteristic_size = characteristic_length*size_factor
        bbox_size = stl_bbox.size

        if (internal_flow):
            domain_bbox = stl_bbox.scale_dimensions(-0.1*bbox_size[0]*size_factor, 0.1*bbox_size[0]*size_factor, -0.1*bbox_size[1]*size_factor, 0.1*bbox_size[1]*size_factor, -0.1*bbox_size[2]*size_factor, 0.1*bbox_size[2]*size_factor)
        else:
            domain_bbox = stl_bbox.scale_dimensions(-3*characteristic_size, 9*characteristic_size, -2*characteristic_size, 2*characteristic_size, -2*characteristic_size, 2*characteristic_size)


        if on_ground:  # the the body is touching the ground
            domain_bbox.minz = stl_bbox.minz
            domain_bbox.maxz = stl_bbox.maxz + 4.0*characteristic_size
        
        if is_half_model:
            domain_bbox.maxy = (domain_bbox.maxy+domain_bbox.miny)/2.
        return domain_bbox


    # to calculate the refinement box for snappyHexMeshDict
    @staticmethod
    def get_refinement_box(stl_bbox: BoundingBox):
        x_length, y_length, z_length = stl_bbox.size
        return stl_bbox.scale_dimensions(-0.7*x_length, 15.0*x_length, -1.0*y_length, 1.0*y_length, -1.0*z_length, 1.0*z_length)

    @staticmethod
    def get_refinement_box_close(stl_bbox: BoundingBox):
        x_length, y_length, z_length = stl_bbox.size
        return stl_bbox.scale_dimensions(-0.2*x_length, 3.0*x_length, -0.45*y_length, 0.45*y_length, -0.45*z_length, 0.45*z_length)

    # to add refinement box to mesh settings
    @staticmethod
    def get_refinement_boxes(stl_bbox: BoundingBox, boxName='refinementBox', ref_level=2, is_internal_flow=False) -> dict[str, SearchableBoxGeometry]:
        if (is_internal_flow):
            return {}
        box = StlAnalysis.get_refinement_box(stl_bbox)
        fineBox = StlAnalysis.get_refinement_box_close(stl_bbox)
        return {
            boxName: SearchableBoxGeometry(
                type='searchableBox',
                bbox=box,
                refineMax=ref_level-1
            ), 
            "fineBox": SearchableBoxGeometry(
                type='searchableBox',
                bbox=fineBox,
                refineMax=ref_level
            )
        }
       
    # refinement box for the ground for external automotive flows
    @staticmethod
    def get_ground_refinement_box(mesh_settings: MeshSettings, stl_bbox: BoundingBox, refLevel=2):
        z = mesh_settings.domain.minz
        z_delta = 0.2*(stl_bbox.maxz-stl_bbox.minz)
        box = BoundingBox(minx=-1000.0, maxx=1000., miny=-1000, maxy=1000, minz=z-z_delta, maxz=z+z_delta)
        return SearchableBoxGeometry(
            type='searchableBox',
            bbox=box,
            refineMax=refLevel
        )

    # to calculate nearest wall thickness for a target yPlus value
    @staticmethod
    def calc_y(nu=1e-6, rho=1000., L=1.0, U_val=1.0, target_yPlus=200):
        Re = U_val*L/nu
        Cf = 0.0592*Re**(-1./5.)
        tau = 0.5*rho*Cf*U_val**2.
        uStar = np.sqrt(tau/rho)
        y = target_yPlus*nu/uStar
        return y

    # to calculate yPlus value for a given first layer thickness
    @staticmethod
    def calc_yPlus(nu=1e-6, L=1.0, u=1.0, y=0.001):
        Re = u*L/nu
        Cf = 0.0592*Re**(-1./5.)
        tau = 0.5*Cf*u**2.
        uStar = np.sqrt(tau)
        yPlus = uStar*y/nu
        return yPlus

    # calculate nearest cell size for a given expansion ratio and layer count
    @staticmethod
    def calc_cell_size(y_=0.001, nLayers=5, expRatio=1.2, thicknessRatio=0.3):
        max_y = y_*expRatio**(nLayers)
        return max_y/thicknessRatio

    @staticmethod
    def calc_refinement_levels(max_cell_size=0.1, target_cell_size=0.001):
        size_ratio = max_cell_size / target_cell_size
        n = np.log(size_ratio)/np.log(2.)
        # print(n)
        return int(np.ceil(n))

    @staticmethod
    def calc_nx_ny_nz(domain_bbox: BoundingBox, target_cell_size: float):
        domain_size = domain_bbox.size
        nx = domain_size[0]/target_cell_size
        ny = domain_size[1]/target_cell_size
        nz = domain_size[2]/target_cell_size
        nx, ny, nz = int(math.ceil(nx)), int(math.ceil(ny)), int(math.ceil(nz))
        # it is better to have even number of cells
        if nx % 2:  # if nx is odd
            nx += 1
        if ny % 2:  # if ny is odd
            ny += 1
        if nz % 2:  # if nz is odd
            nz += 1
        return (nx, ny, nz)

    # Function to read STL file and compute bounding box
    @staticmethod
    def compute_bounding_box(mesh: vtk.vtkPolyData):
        # Calculate the bounding box
        bounds = mesh.GetBounds()
        return BoundingBox(minx=bounds[0], maxx=bounds[1], miny=bounds[2], maxy=bounds[3], minz=bounds[4], maxz=bounds[5])

    # this is the wrapper function to check if a point is inside the mesh
    @staticmethod
    def is_point_inside(stl_file_path, point):
        # Check if the file exists
        if not os.path.exists(stl_file_path):
            raise FileNotFoundError(
                f"File not found: {stl_file_path}. Make sure the file exists.")
        # Create a reader for the STL file
        reader = vtk.vtkSTLReader()
        reader.SetFileName(stl_file_path)
        reader.Update()

        # Get the output data from the reader
        poly_data = reader.GetOutput()
        # Calculate the bounding box
        bounds = poly_data.GetBounds()
        # Check if the point is inside the bounding box
        xmin, xmax, ymin, ymax, zmin, zmax = bounds
        if point[0] < xmin or point[0] > xmax:
            return False
        if point[1] < ymin or point[1] > ymax:
            return False
        if point[2] < zmin or point[2] > zmax:
            return False
        # Check if the point is inside the mesh
        return is_point_inside(poly_data, point)

    @staticmethod
    def calc_nLayer(yFirst=0.001, targetCellSize=0.1, expRatio=1.2):
        n = np.log(targetCellSize*0.4/yFirst)/np.log(expRatio)
        return int(np.ceil(n))


    @staticmethod
    # calculates N layers and final layer thickness
    # yFirst: first layer thickness
    # delta: boundary layer thickness
    # expRatio: expansion ratio
    def calc_layers(yFirst=0.001, delta=0.01, expRatio=1.2):
        currentThickness = yFirst*2.0  # initial thickness. Twice the yPlus value
        currentDelta = 0
        N = 0
        for i in range(1, 50):
            currentThickness = currentThickness*expRatio**(i)
            currentDelta = currentDelta + currentThickness
            if (currentDelta > delta):
                N = i
                break
        finalLayerThickness = currentThickness

        return N, finalLayerThickness


    # this function calculates the smallest curvature of the mesh
    # This function calls stlToOpenFOAM functions to read the mesh and calculate curvature

    @staticmethod
    def calc_smallest_curvature(mesh: vtk.vtkPolyData):
        curved_mesh = compute_curvature(mesh, curvature_type='mean')
        curvature_values = extract_curvature_data(curved_mesh)
        return np.min(curvature_values)

    @staticmethod
    def calc_background_cell_size(refinement_amount: RefinementAmount, stl_bbox: BoundingBox, maxCellSize: float, internalFlow: bool):
        max_length = stl_bbox.max_length
        min_length = stl_bbox.min_length
        
        if (refinement_amount == "coarse"):
            if (internalFlow):
                if max_length/min_length > 10:  # if the geometry is very slender
                    return min(max_length/50., maxCellSize)
                else:
                    return min(min_length/8., maxCellSize)
            else:
                # this is the size of largest blockMesh cells
                return min(min_length/3., maxCellSize)
        elif (refinement_amount == "medium"):
            if (internalFlow):
                if max_length/min_length > 10:  # if the geometry is very slender
                    return min(max_length/70., maxCellSize)
                else:
                    return min(min_length/12., maxCellSize)
            else:
                return min(min_length/5., maxCellSize)
        else:
            if (internalFlow):
                if max_length/min_length > 10:  # if the geometry is very slender
                    return min(max_length/90., maxCellSize)
                else:
                    return min(min_length/16., maxCellSize)
            else:
                return min(min_length/7., maxCellSize)



    @staticmethod
    def calc_domain(stl_bbox: BoundingBox, settings: SimulationSettings, max_cell_size=2.0, size_factor=1.0):
        characteristic_length = stl_bbox.max_length

        if (max_cell_size < 0.001):
            max_cell_size = characteristic_length/4.

        domain_size = StlAnalysis.calc_domain_bbox(stl_bbox, size_factor, settings.mesh.onGround, settings.mesh.internalFlow, settings.mesh.halfModel)
        if (max_cell_size < 0.001):
            max_cell_size = characteristic_length/4.
        background_cell_size = StlAnalysis.calc_background_cell_size(settings.mesh.refAmount, stl_bbox, max_cell_size, settings.mesh.internalFlow)
        nx, ny, nz = StlAnalysis.calc_nx_ny_nz(domain_size, background_cell_size)
        return Domain.from_bbox(domain_size, nx, ny, nz)


    @staticmethod
    def calc_boundary_layer(stl_bbox: BoundingBox, settings: SimulationSettings, target_cell_size: float):
        characteristic_length = stl_bbox.max_length

        target_yPlus = {
            "coarse": 70,
            "medium": 50,
            "fine": 30,
        }[settings.mesh.refAmount]
        
        # this is the thickness of closest cell
        target_y = StlAnalysis.calc_y(
            settings.physicalProperties.nu, 
            settings.physicalProperties.rho, 
            characteristic_length, 
            U_val=settings.boundaryConditions.velocityInlet.u_max, 
            target_yPlus=target_yPlus
        )
        
        first_layer_thickness = target_y*2.0
        final_layer_thickness = target_cell_size*0.35

        num_layers = max(1, int(np.log(final_layer_thickness / first_layer_thickness)/np.log(settings.mesh.addLayersControls.expansionRatio)))

    
        return BoundaryLayer(
            yPlus=target_yPlus, 
            y=target_y, 
            first_layer_thickness=first_layer_thickness, 
            final_layer_thickness=final_layer_thickness, 
            nLayers=num_layers
        )

    @staticmethod
    def calc_center_of_mass(mesh: vtk.vtkPolyData):
        center_of_mass_filter = vtk.vtkCenterOfMass()
        center_of_mass_filter.SetInputData(mesh)
        center_of_mass_filter.Update()
        center_of_mass = center_of_mass_filter.GetCenter()
        return center_of_mass

    @staticmethod
    def get_location_in_mesh(mesh: vtk.vtkPolyData, is_internal_flow: bool) -> tuple[float, float, float]:
        center_of_mass = StlAnalysis.calc_center_of_mass(mesh)
        outside_point = StlAnalysis.get_outside_point(mesh)
        inside_point = find_inside_point(mesh, center_of_mass, min_bounds=None, max_bounds=None)
        return tuple(inside_point if is_internal_flow else outside_point) # type: ignore
        
    @staticmethod 
    def set_stl_solid_name(stl_file: Union[str, Path]) -> int:
        stl_path = Path(stl_file)
        IOUtils.print(f"Setting solid name for {stl_path}")
        
        if not stl_path.exists():
            raise FileNotFoundError(f"STL file not found: {stl_path}")

        if not stl_path.is_file():
            raise ValueError(f"Path is not a file: {stl_path}")

        # Extract solid name from filename without extension
        solid_name = stl_path.stem

        # Read and process file contents
        lines = stl_path.read_text().splitlines()
        new_lines = []
        for line in lines:
            if 'endsolid' in line.lower():
                line = f"endsolid {solid_name}"
            elif line.lower().lstrip().startswith('solid'):
                line = f"solid {solid_name}"
            new_lines.append(line + '\n')
        
        # Write back to file
        stl_path.write_text(''.join(new_lines))
        return 0

    

    @staticmethod
    def get_outside_point(mesh: vtk.vtkPolyData):
        stl_bbox = StlAnalysis.compute_bounding_box(mesh)
        outsideX = stl_bbox.maxx + 0.05*(stl_bbox.maxx-stl_bbox.minx)
        outsideY = stl_bbox.miny*0.95  # (stlMaxY - stlMinY)/2.
        outsideZ = (stl_bbox.maxz - stl_bbox.minz)/2.
        outsidePoint = (outsideX, outsideY, outsideZ)
        return outsidePoint


    @staticmethod
    def add_stl_to_settings(settings: SimulationSettings, stl_path: Union[str, Path], type: PatchType, property: PatchProperty):
        stl_name = Path(stl_path).name
        stl_mesh = read_stl_file(str(stl_path))
        stl_bbox = StlAnalysis.compute_bounding_box(stl_mesh)

        # Skip feature edges for refinement regions
        feature_edges = type not in ('refinementRegion', 'refinementSurface')
        
        ref_level = {
            "coarse": 2,
            "medium": 4,
            "fine": 6,
        }[settings.mesh.refAmount]

        if (type == "wall"):
            # TODO: make this apply for multiple stl files in future
            for geometry in settings.mesh.geometry.values():
                if geometry.type == "wall":
                    raise ValueError("Only one wall geometry entry allowed currently, if multiple please fuse with one STL")

            stl_domain = StlAnalysis.calc_domain(stl_bbox, settings)
            settings.mesh.domain = Domain.expand_domain(settings.mesh.domain, stl_domain)


            background_cell_size = abs((stl_domain.maxx-stl_domain.minx)/stl_domain.nx)
            target_cell_size = background_cell_size/2.**ref_level
            boundary_layer = StlAnalysis.calc_boundary_layer(stl_bbox, settings, target_cell_size)
            n_layer = boundary_layer.nLayers

            # store the background mesh size for future reference
            settings.mesh.maxCellSize = background_cell_size


            settings.mesh.castellatedMeshControls.locationInMesh = StlAnalysis.get_location_in_mesh(stl_mesh, settings.mesh.internalFlow)
            
            box_ref_level = max(2, ref_level-3)
            refinement_boxes = StlAnalysis.get_refinement_boxes(stl_bbox, ref_level=box_ref_level, is_internal_flow=settings.mesh.internalFlow)
            settings.mesh.geometry.update(refinement_boxes)
            if (not settings.mesh.internalFlow and settings.mesh.onGround):
                # if the flow is external and the geometry is on the ground, add a ground refinement box
                settings.mesh.geometry["groundBox"] = StlAnalysis.get_ground_refinement_box(settings.mesh, stl_bbox, box_ref_level)
            
            ref_min = max(1, ref_level)
            ref_max = max(2, ref_level)
            feature_level =  max(ref_level, 1)

            # set the layer thickness to 0.5 times the cell size
            settings.mesh.addLayersControls.finalLayerThickness = 0.5
            minThickness = max(0.0001, settings.mesh.addLayersControls.finalLayerThickness/100.)
            settings.mesh.addLayersControls.minThickness = minThickness

            characteristic_length = stl_bbox.max_length        
            reynolds_number = TurbulenceUtils.calc_renolds_number(U=settings.boundaryConditions.velocityInlet.u_max, L=characteristic_length, nu=settings.physicalProperties.nu)
            delta = TurbulenceUtils.calc_delta(reynolds_number, characteristic_length)


            IOUtils.print("\n-----------------Turbulence-----------------")
            IOUtils.print(f"Target yPlus:{boundary_layer.yPlus}")
            IOUtils.print(f'Reynolds number:{reynolds_number}')
            IOUtils.print(f"Boundary layer thickness: {delta}")
            IOUtils.print(f"Final layer thickness:{boundary_layer.final_layer_thickness}")
            IOUtils.print(f"Number of layers:{boundary_layer.nLayers}")


            # print the summary of results
            IOUtils.print("\n-----------------Mesh Settings-----------------")
            IOUtils.print(stl_domain.__repr__())
            IOUtils.print(f"Max cell size: {background_cell_size}")
            IOUtils.print(f"Min cell size: {target_cell_size}")
            IOUtils.print(f"Refinement Level:{ref_level}")


        
        else:
            n_layer = {
                "coarse": 2,
                "medium": 4,
                "fine": 6,
            }[settings.mesh.refAmount]
            ref_min = 0
            ref_max = 0
            feature_level = 1


        for geometry in settings.mesh.geometry.values():
            if (isinstance(geometry, TriSurfaceMeshGeometry)):
                ref_min = max(ref_min, geometry.refineMin)
                feature_level = max(feature_level, geometry.featureLevel)
                ref_max = max(ref_max, geometry.refineMax)

        settings.mesh.geometry[stl_name] = TriSurfaceMeshGeometry(
            type=type,
            refineMin=ref_min,
            refineMax=ref_max,
            featureEdges=feature_edges,
            featureLevel=feature_level,
            nLayers=n_layer,
            property=property,
            bounds=stl_bbox
        )

        return settings.mesh



