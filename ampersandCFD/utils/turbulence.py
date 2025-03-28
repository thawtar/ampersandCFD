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

from typing import Union


class TurbulenceUtils:
    @staticmethod
    def kEpsilon(U: float, nu: float, I: float = 0.16) -> tuple[float, float, float]:
        """
        Calculate turbulence parameters k, epsilon and omega using the k-epsilon model.

        The k-epsilon model is used to initialize turbulent flow parameters based on 
        inlet velocity and turbulence intensity.

        Parameters
        ----------
        U : float
            Inlet velocity magnitude [m/s]
        nu : float
            Kinematic viscosity [m²/s]
        I : float, optional
            Turbulence intensity, default is 0.16 (16%)

        Returns
        -------
        tuple[float, float, float]
            Tuple containing:
            - k: Turbulent kinetic energy [m²/s²]
            - epsilon: Turbulent dissipation rate [m²/s³] 
            - omega: Specific dissipation rate [1/s]

        Notes
        -----
        The model uses standard coefficients:
        - C_mu = 0.09 for the relationship between k and epsilon
        """
        k = 1.5 * (U * I) ** 2
        epsilon = 1.5 * k ** 1.5 / (0.09 * nu)
        omega = 0.09 * k / epsilon
        return k, epsilon, omega

    @staticmethod
    def calc_intensity(U: float, nu: float, D: float) -> float:
        Re = U * D / nu
        I = 0.16 * Re ** (-1. / 8.)
        return I

    @staticmethod
    def calc_length_scale(D: float) -> float:
        return 0.07 * D

    @staticmethod
    def calc_length_scale_channel(W: float, H: float) -> float:
        A = W * H
        P = 2 * (W + H)
        D = 4 * A / P
        l = 0.07 * D
        return l

    @staticmethod
    def calc_k(U: Union[float, tuple[float, float, float]], I: float) -> float:
        U_mag = U if isinstance(U, float) else sum([el**2 for el in U])**0.5
        return 1.5 * (U_mag * I) ** 2

    @staticmethod
    def calc_epsilon(k: float, l: float) -> float:
        Cmu = 0.09
        eps = Cmu ** (3. / 4.) * k ** (3. / 2.) / l
        return eps

    @staticmethod
    def calc_omega(k: float, l: float) -> float:
        Cmu = 0.09
        omega = Cmu ** (-1. / 4.) * k ** 0.5 / l
        return omega

  

    @staticmethod
    def calc_renolds_number(U: float, L: float, nu: float) -> float:
        return U*L/nu
    
    @staticmethod
    def calc_delta(Re: float, L=1.0):
        return 0.37*L/Re**(0.2)
