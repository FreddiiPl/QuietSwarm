import ctypes
import os

base_path = os.path.dirname(__file__)
so_path = os.path.join(base_path,'..','Propagation', 'propagate.so')
lib = ctypes.CDLL(so_path)

class OrbitalParameters(ctypes.Structure):
            _fields_ = [
                ("rightAscensionOfAscendingNode", ctypes.c_double),
                ("argumentOfPerigee", ctypes.c_double),
                ("inclinationAngle", ctypes.c_double),
                ("phaseAngles", ctypes.c_double),
                ("semiMajorAxis", ctypes.c_double),
                ("eccentricity", ctypes.c_double),
            ]


class objectTypes:
    def __init__(self,):
        self.int_type    = ctypes.c_int
        self.double_type = ctypes.c_double
        self.double_ptr  = ctypes.POINTER(ctypes.c_double)
        self.bool_type   = ctypes.c_bool
        
        
    
    
    def propagator_c(self,):
        self.orbit_param = OrbitalParameters
        
        lib.propagate.argtypes = [
            self.int_type,
            self.double_type,
            self.int_type,
            ctypes.POINTER(OrbitalParameters),
            self.bool_type
        ]
        
        return lib
    