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
from ampersandCFD.models.settings import NumericalSettings, SolverSettings
from ampersandCFD.utils.generation import GenerationUtils

class FVDictGenerator:
    @staticmethod
    def generate_algorithmDict(numerical_settings: NumericalSettings):
        algorithmDict = f"""
    PIMPLE
    {{
        nOuterCorrectors {numerical_settings.pimpleDict.nOuterCorrectors};
        nCorrectors {numerical_settings.pimpleDict.nCorrectors};
        nNonOrthogonalCorrectors {numerical_settings.pimpleDict.nNonOrthogonalCorrectors};
        pRefCell {numerical_settings.pimpleDict.pRefCell};
        pRefValue {numerical_settings.pimpleDict.pRefValue};
        residualControl
        {{
            "(U|k|omega|epsilon|nut)"
            {{
                tolerance {numerical_settings.pimpleDict.residualControl.U};
                relTol 0;
            }}
            p
            {{
                tolerance {numerical_settings.pimpleDict.residualControl.p};
                relTol 0;
            }}
        }}
    }}
    SIMPLE
    {{
        nNonOrthogonalCorrectors {numerical_settings.simpleDict.nNonOrthogonalCorrectors};
        consistent {numerical_settings.simpleDict.consistent};
        residualControl
        {{
            U {numerical_settings.simpleDict.residualControl.U};
            p {numerical_settings.simpleDict.residualControl.p};
            k {numerical_settings.simpleDict.residualControl.k};
            omega {numerical_settings.simpleDict.residualControl.omega};
            epsilon {numerical_settings.simpleDict.residualControl.epsilon};
            nut {numerical_settings.simpleDict.residualControl.nut};
        }}
    }}
    potentialFlow
    {{
        nNonOrthogonalCorrectors {numerical_settings.potentialFlowDict.nonOrthogonalCorrectors};
    }}
    relaxationFactors
    {{
        equations
        {{
            U {numerical_settings.relaxationFactors.U};

            k {numerical_settings.relaxationFactors.k};
            omega {numerical_settings.relaxationFactors.omega};
            epsilon {numerical_settings.relaxationFactors.epsilon};
            nut {numerical_settings.relaxationFactors.nut};
        }}
        fields
        {{
            p {numerical_settings.relaxationFactors.p};
        }}
    }}
    """
        return algorithmDict


    @staticmethod
    def generate_solverDict(solverSettings: SolverSettings, solverName="U"):
        solverCfg = getattr(solverSettings, solverName)
        solverDict = f""
        if (solverName == "p" or solverName == "Phi" or solverName == "p_rgh"):
            solverDict += f"""
    {solverName}
    {{
        solver {solverCfg["type"]};
        smoother {solverCfg["smoother"]};
        agglomerator {solverCfg["agglomerator"]};
        nCellsInCoarsestLevel {solverCfg["nCellsInCoarsestLevel"]};
        mergeLevels {solverCfg["mergeLevels"]};
        cacheAgglomeration {solverCfg["cacheAgglomeration"]};
        tolerance {solverCfg["tolerance"]};
        relTol {solverCfg["relTol"]};
        maxIter {solverCfg["maxIter"]};
        nSweeps {solverCfg["nSweeps"]};
        nPreSweeps {solverCfg["nPreSweeps"]};
    }}
    """
        else:
            solverDict += f"""
    {solverName}
    {{
        solver {solverCfg["type"]};
        smoother {solverCfg["smoother"]};
        tolerance {solverCfg["tolerance"]};
        relTol {solverCfg["relTol"]};
        maxIter 100;
    }}
    """
        return solverDict


    @staticmethod
    def generate_solverFinalDict(solverSettings: SolverSettings, solverName="U"):
        solverDict = f"""
        {solverName}Final
        {{
            ${solverName}
            tolerance {getattr(solverSettings, solverName)["tolerance"]/100.};
            relTol 0;
        }}
        """
        return solverDict


    @staticmethod
    def generate_fvsolution(numerical_settings: NumericalSettings, solverSettings: SolverSettings):
        fvSolutionDict = f"""{GenerationUtils.createFoamHeader("dictionary", "fvSolution")}
    solvers
    {{
        """
        for solver in solverSettings.model_fields.keys():
            fvSolutionDict += FVDictGenerator.generate_solverDict(solverSettings, solver)
            fvSolutionDict += FVDictGenerator.generate_solverFinalDict(solverSettings, solver)
        fvSolutionDict += f"""
    }}
        """
        fvSolutionDict += FVDictGenerator.generate_algorithmDict(numerical_settings)
        return fvSolutionDict


    @staticmethod
    def generate_fvSchemesDict(numerical_settings: NumericalSettings):
        fvSchemesDict = f"""{GenerationUtils.createFoamHeader("dictionary", "fvSchemes")}
    ddtSchemes
    {{
        default {numerical_settings.ddtSchemes.default};
    }}
    gradSchemes
    {{
        default {numerical_settings.gradSchemes.default};
        grad(p) {numerical_settings.gradSchemes.grad_p};
        grad(U) {numerical_settings.gradSchemes.grad_U};
    }}
    divSchemes
    {{
        default {numerical_settings.divSchemes.default};
        div(phi,U) {numerical_settings.divSchemes.div_phi_U};
        div(phi,k) {numerical_settings.divSchemes.div_phi_k};
        div(phi,omega) {numerical_settings.divSchemes.div_phi_omega};
        div(phi,epsilon) {numerical_settings.divSchemes.div_phi_epsilon};
        div(phi,nut) {numerical_settings.divSchemes.div_phi_nut};
        div(nuEff*dev(T(grad(U)))) {numerical_settings.divSchemes.div_nuEff_dev_T_grad_U};
    }}
    laplacianSchemes
    {{
        default {numerical_settings.laplacianSchemes.default};
    }}
    interpolationSchemes
    {{
        default {numerical_settings.interpolationSchemes.default};
    }}
    snGradSchemes
    {{
        default {numerical_settings.snGradSchemes.default};
    }}
    fluxRequired
    {{
        default {numerical_settings.fluxRequired.default};
    }}
    wallDist
    {{
        method {numerical_settings.wallDist};
    }}
    """
        return fvSchemesDict



    @staticmethod
    def generate_fvSchemes(numerical_settings: NumericalSettings):
        fvSchemesDict = f"""{GenerationUtils.createFoamHeader("dictionary", "fvSchemes")}
    ddtSchemes
    {{
        default {numerical_settings.ddtSchemes.default};
    }}
    gradSchemes
    {{
        default {numerical_settings.gradSchemes.default};
        grad(p) {numerical_settings.gradSchemes.grad_p};
        grad(U) {numerical_settings.gradSchemes.grad_U};
    }}
    divSchemes
    {{
        default {numerical_settings.divSchemes.default};
        div(phi,U) {numerical_settings.divSchemes.div_phi_U};
        div(phi,k) {numerical_settings.divSchemes.div_phi_k};
        div(phi,omega) {numerical_settings.divSchemes.div_phi_omega};
        div(phi,epsilon) {numerical_settings.divSchemes.div_phi_epsilon};
        div(phi,nut) {numerical_settings.divSchemes.div_phi_nut};
        div(nuEff*dev(T(grad(U)))) {numerical_settings.divSchemes.div_nuEff_dev_T_grad_U};
    }}
    laplacianSchemes
    {{
        default {numerical_settings.laplacianSchemes.default};
    }}
    interpolationSchemes
    {{
        default {numerical_settings.interpolationSchemes.default};
    }}
    snGradSchemes
    {{
        default {numerical_settings.snGradSchemes.default};
    }}
    fluxRequired
    {{
        default {numerical_settings.fluxRequired.default};
    }}
    wallDist
    {{
        method {numerical_settings.wallDist};
    }}
    """
        return fvSchemesDict

    @staticmethod
    def write(numerical_settings: NumericalSettings, solver_settings: SolverSettings, project_path: Union[str, Path]):
        fvSchemesDict = FVDictGenerator.generate_fvSchemes(numerical_settings)
        Path(f"{project_path}/system/fvSchemes").write_text(fvSchemesDict)        

        fvSolutionDict = FVDictGenerator.generate_fvsolution(numerical_settings, solver_settings)
        Path(f"{project_path}/system/fvSolution").write_text(fvSolutionDict)
        