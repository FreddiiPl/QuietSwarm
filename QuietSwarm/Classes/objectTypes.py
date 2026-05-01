import ctypes
import os

base_path = os.path.dirname(__file__)
so_path = os.path.join(base_path, 'c_functions', 'propagator.so')
lib = ctypes.CDLL(so_path)


class objectTypes:
    def __init__(self,):
        self.int_type    = ctypes.c_int
        self.double_type = ctypes.c_double
        self.double_ptr  = ctypes.POINTER(ctypes.c_double)
        
        
        # for now
        class OrbitalParameters(ctypes.Structure):
            _fields_ = [
                ("rightAscensionOfAscendingNode", ctypes.c_double),
                ("argumentOfPerigee", ctypes.c_double),
                ("inlinationAngle", ctypes.c_double),
                ("phaseAngles", ctypes.c_double),
                ("semiMajorAxis", ctypes.c_double),
                ("eccentricity", ctypes.c_double),
            ]
        
        
        self.OrbitalParameters = OrbitalParameters
    
    
    
    
    def propagator_c(self,):
        lib.propagate.argtypes = [
            self.int_type,
            self.double_type,
            self.OrbitalParameters
        ]
        
        return lib
    