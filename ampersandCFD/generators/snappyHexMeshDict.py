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

from pathlib import Path
from typing import Union
from ampersandCFD.models.settings import SearchableBoxGeometry, TriSurfaceMeshGeometry, SnappyHexMeshSettings
from ampersandCFD.utils.generation import GenerationUtils

class SnappyHexMeshDictGenerator:
    @staticmethod    
    def generate(mesh_settings: SnappyHexMeshSettings):
        """
        Create a snappyHexMeshDict for OpenFOAM.

        Parameters:
        stl_files (list): A list of STL file names.
        refinement_levels (dict): A dictionary where keys are STL file names and values are refinement levels.
        layer_counts (dict): A dictionary where keys are STL file names and values are layer counts.

        Returns:
        str: The content of the snappyHexMeshDict file as a string.
        """
        snappyHexMeshDict = f""
        trueFalse = {True: "true", False: "false"}
        header = GenerationUtils.createFoamHeader(
            className="dictionary", objectName="snappyHexMeshDict")

        steps = f"""
    castellatedMesh {mesh_settings.snappyHexSteps.castellatedMesh};
    snap            {mesh_settings.snappyHexSteps.snap};
    addLayers       {mesh_settings.snappyHexSteps.addLayers};"""

        features = ""
        refinementSurfaces = ""
        added_geo = ""
        # maxRefinementLevel = 1
        # minRefinementRegionLevel = 2
        geometry_str = f"""\ngeometry\n{{"""
        for geometry_name, geometry in mesh_settings.geometry.items():
            patch_name = geometry_name.split('.')[0]

            # For STL surfaces, featureEdges and refinementSurfaces are added
            # maxRefinementLevel = max(maxRefinementLevel, geometry_patch.refineMax)
            if (isinstance(geometry, TriSurfaceMeshGeometry)):
                added_geo = f"""\n
        {geometry_name}
        {{
            type triSurfaceMesh;
            name {patch_name};
            regions
            {{
                {patch_name}
                {{
                    name {patch_name};
                }}
            }}
        }}"""
                # Add features and refinement surfaces
                if (geometry.featureEdges):
                    features += f"""

            {{
                file \"{patch_name}.eMesh\";
                level {geometry.featureLevel};
            }}"""
                if (geometry.type == 'inlet' or geometry.type == 'outlet'):
                    patchType = 'patch'
                    refinementSurfaces += f"""
            {patch_name}
            {{
                level (0 0);
                regions
                {{
                    {patch_name}
                    {{
                        level ({geometry.refineMin} {geometry.refineMax});
                        patchInfo
                        {{
                            type {patchType};
                        }}
                    }}
                }}
            }}"""
                elif (geometry.type == 'cellZone'):
                    patchType = 'cellZone'
                    if geometry.property[1] == True:  # patches will be added
                        refinementSurfaces += f"""
            {patch_name}
            {{
                level (0 0);
                cellZone {patch_name};
                faceZone {patch_name};
                cellZoneInside inside;
                boundary internal;
                faceType boundary;
            }}"""
                    else:  # no patches. Just cellZone
                        refinementSurfaces += f"""
            {patch_name}
            {{
                level (0 0);
                cellZone {patch_name};
                faceZone {patch_name};
                cellZoneInside inside;
                boundary internal;
            }}"""
                    # if refinementSurface or region, do not add here
                elif (geometry.type == 'refinementRegion' or geometry.type == 'refinementSurface'):
                    pass

                elif (geometry.type == 'baffle'):
                    patchType = 'wall'
                    refinementSurfaces += f"""
            {patch_name}
            {{
                level (0 0);
                regions
                {{
                    {patch_name}
                    {{
                        faceType baffles;
                        faceZone {patch_name};
                        level ({geometry.refineMin} {geometry.refineMax});
                    }}
                }}
            }}"""

                else:
                    patchType = 'wall'
                    refinementSurfaces += f"""
            {patch_name}
            {{
                level (0 0);
                regions
                {{
                    {patch_name}
                    {{
                        level ({geometry.refineMin} {geometry.refineMax});
                        patchInfo
                        {{
                            type {patchType};
                        }}
                    }}
                }}
            }}"""

            # For searchable boxes, min and max are added
            elif (isinstance(geometry, SearchableBoxGeometry)):
                added_geo = f"""
        {geometry_name}
        {{
            type searchableBox;
            min ({geometry.bbox.minx} {geometry.bbox.miny} {geometry.bbox.minz});
            max ({geometry.bbox.maxx} {geometry.bbox.maxy} {geometry.bbox.maxz});
        }}"""
            geometry_str += added_geo
        geometry_str += f"""

    }}"""

        refinementRegions = f""
        for geometry_name, geometry in mesh_settings.geometry.items():
            patch_name = geometry_name.split('.')[0]
            if (isinstance(geometry, SearchableBoxGeometry)):
                refinementRegions += f"""
            {geometry_name}
            {{
                mode inside;
                levels ((1E15 {geometry.refineMax}));
            }}"""
            elif (isinstance(geometry, TriSurfaceMeshGeometry)):
                if (geometry.type == 'refinementSurface'):
                    refinementRegions += f"""
            {patch_name}
            {{
                mode distance;
                levels ((1E-4 {geometry.property}));
            }}"""
                elif (geometry.type == 'refinementRegion'):
                    refinementRegions += f"""
            {patch_name}
            {{
                mode inside;
                levels ((1E15 {geometry.property}));
            }}"""
                elif (geometry.type == 'cellZone'):
                    refinementRegions += f"""
            {patch_name}
            {{
                mode inside;
                levels ((1E15 {geometry.property[0]}));
            }}"""

            else:
                pass

        castellatedMeshControls = f"""\ncastellatedMeshControls
    {{
        maxLocalCells {mesh_settings.castellatedMeshControls.maxLocalCells};
        maxGlobalCells {mesh_settings.castellatedMeshControls.maxGlobalCells};
        minRefinementCells {mesh_settings.castellatedMeshControls.minRefinementCells};
        maxLoadUnbalance {mesh_settings.castellatedMeshControls.maxLoadUnbalance};
        nCellsBetweenLevels {mesh_settings.castellatedMeshControls.nCellsBetweenLevels};
        features
        (
            {features}
        );
        refinementSurfaces
        {{
            {refinementSurfaces}
        }}
        resolveFeatureAngle {mesh_settings.castellatedMeshControls.resolveFeatureAngle};
        refinementRegions
        {{
            {refinementRegions}
        }};
        locationInMesh ({mesh_settings.castellatedMeshControls.locationInMesh[0]} {mesh_settings.castellatedMeshControls.locationInMesh[1]} {mesh_settings.castellatedMeshControls.locationInMesh[2]});
        allowFreeStandingZoneFaces {mesh_settings.castellatedMeshControls.allowFreeStandingZoneFaces};
    }}"""

        snapControls = f"""\nsnapControls
    {{
        nSmoothPatch {mesh_settings.snapControls.nSmoothPatch};
        tolerance {mesh_settings.snapControls.tolerance};
        nSolveIter {mesh_settings.snapControls.nSolveIter};
        nRelaxIter {mesh_settings.snapControls.nRelaxIter};
        nFeatureSnapIter {mesh_settings.snapControls.nFeatureSnapIter};
        implicitFeatureSnap {mesh_settings.snapControls.implicitFeatureSnap};
        explicitFeatureSnap {mesh_settings.snapControls.explicitFeatureSnap};
        multiRegionFeatureSnap {mesh_settings.snapControls.multiRegionFeatureSnap};
    }}"""
        layerControls = f"""\naddLayersControls
    {{
        relativeSizes {mesh_settings.addLayersControls.relativeSizes};
        layers
        {{"""
        for geometry_name, geometry in mesh_settings.geometry.items():
            patch_name = geometry_name.split('.')[0]
            if (isinstance(geometry, TriSurfaceMeshGeometry)):
                if (geometry.type == 'wall'):  # If the surface is a wall, add layers
                    layerControls += f"""
                "{patch_name}.*"
                {{
                    nSurfaceLayers {geometry.nLayers};
                }}"""
                elif (geometry.type == 'baffle'):  # If the surface is a baffle, add layers
                    layerControls += f"""
                "{patch_name}.*"
                {{
                    nSurfaceLayers {1};
                }}"""
                elif (geometry.type == 'cellZone'):
                    layerControls += f"""
                "{patch_name}.*"
                {{
                    nSurfaceLayers {1};
                }}"""
                else:
                    pass
        layerControls += f"""
        }};
        expansionRatio {mesh_settings.addLayersControls.expansionRatio};
        finalLayerThickness {mesh_settings.addLayersControls.finalLayerThickness};
        //firstLayerThickness {mesh_settings.addLayersControls.firstLayerThickness};
        minThickness {mesh_settings.addLayersControls.minThickness};
        nGrow {mesh_settings.addLayersControls.nGrow};
        featureAngle {mesh_settings.addLayersControls.featureAngle};
        slipFeatureAngle {mesh_settings.addLayersControls.slipFeatureAngle};
        nRelaxIter {mesh_settings.addLayersControls.nRelaxIter};
        nSmoothSurfaceNormals {mesh_settings.addLayersControls.nSmoothSurfaceNormals};
        nSmoothNormals {mesh_settings.addLayersControls.nSmoothNormals};
        nSmoothThickness {mesh_settings.addLayersControls.nSmoothThickness};
        maxFaceThicknessRatio {mesh_settings.addLayersControls.maxFaceThicknessRatio};
        maxThicknessToMedialRatio {mesh_settings.addLayersControls.maxThicknessToMedialRatio};
        minMedianAxisAngle {mesh_settings.addLayersControls.minMedianAxisAngle};
        minMedialAxisAngle {mesh_settings.addLayersControls.minMedianAxisAngle};
        nBufferCellsNoExtrude {mesh_settings.addLayersControls.nBufferCellsNoExtrude};
        nLayerIter {mesh_settings.addLayersControls.nLayerIter};
    }}"""
        meshQualityControls = f"""\nmeshQualityControls
    {{
        maxNonOrtho {mesh_settings.meshQualityControls.maxNonOrtho};
        maxBoundarySkewness {mesh_settings.meshQualityControls.maxBoundarySkewness};
        maxInternalSkewness {mesh_settings.meshQualityControls.maxInternalSkewness};
        maxConcave {mesh_settings.meshQualityControls.maxConcave};
        minVol {mesh_settings.meshQualityControls.minVol};
        minTetQuality {mesh_settings.meshQualityControls.minTetQuality};
        minArea {mesh_settings.meshQualityControls.minArea};
        minTwist {mesh_settings.meshQualityControls.minTwist};
        minDeterminant {mesh_settings.meshQualityControls.minDeterminant};
        minFaceWeight {mesh_settings.meshQualityControls.minFaceWeight};
        minVolRatio {mesh_settings.meshQualityControls.minVolRatio};
        minTriangleTwist {mesh_settings.meshQualityControls.minTriangleTwist};
        nSmoothScale {mesh_settings.meshQualityControls.nSmoothScale};
        errorReduction {mesh_settings.meshQualityControls.errorReduction};
    }}"""
        debug = f"""
    writeFlags
    (
        scalarLevels
        layerSets
        layerFields     // write volScalarField for layer coverage
    );
    debug {mesh_settings.debug};
    mergeTolerance {mesh_settings.mergeTolerance};"""
        snappyHexMeshDict += header+steps+geometry_str+castellatedMeshControls + \
            snapControls+layerControls+meshQualityControls+debug
        return snappyHexMeshDict



    @staticmethod
    def write(mesh_settings: SnappyHexMeshSettings, project_path: Union[str, Path]):
        Path(f"{project_path}/system/snappyHexMeshDict").write_text(SnappyHexMeshDictGenerator.generate(mesh_settings))
