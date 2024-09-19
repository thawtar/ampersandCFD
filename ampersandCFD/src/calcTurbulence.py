import numpy as np
from primitives import ampersandPrimitives, ampersandIO, ampersandDataInput

class calcTurbulence:
    def __init__(self):
        pass

    @staticmethod
    def calc_turbulence_intensity(U=1.0, L=1.0, nu=1e-6):
        return 0.16 * (U * L) / nu
    
    @staticmethod
    def calc_turbulence_length_scale(L=1.0):
        return 0.07 * L
    
    @staticmethod
    def calc_turbulence_viscosity_ratio():
        return 10.0
    
    @staticmethod
    def calc_k(U=1.0, L=1.0, I=0.05):
        return I * (U * L) ** 2
    
    @staticmethod
    def calc_epsilon(U=1.0, L=1.0, k=1.0):
        return 0.09 * k ** 1.5 / (0.07 * L)
    
    @staticmethod
    def calc_nut(U=1.0, L=1.0, k=1.0, epsilon=1.0):
        return k ** 2 / epsilon
    
    @staticmethod
    def calc_Omega(U=1.0, L=1.0):
        return 0.09 * U / L
        