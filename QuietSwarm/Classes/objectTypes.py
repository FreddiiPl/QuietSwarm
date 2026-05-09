import ctypes
import os

base_path = os.path.dirname(__file__)

so_path = os.path.join(base_path,'..','Propagation', 'propagate.so')
lib = ctypes.CDLL(so_path)

so_path_projection = os.path.join(base_path,'..', 'Projections', 'refsystems.so')
lib_projection     = ctypes.CDLL(so_path_projection)

class OrbitalParameters(ctypes.Structure):
            _fields_ = [
                ("rightAscensionOfAscendingNode", ctypes.c_double),
                ("argumentOfPerigee", ctypes.c_double),
                ("inclinationAngle", ctypes.c_double),
                ("phaseAngles", ctypes.c_double),
                ("semiMajorAxis", ctypes.c_double),
                ("eccentricity", ctypes.c_double),
            ]
            

class Output(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("z", ctypes.c_double),
    ]


class objectTypes:
    def __init__(self,):
        self.int_type    = ctypes.c_int
        self.double_type = ctypes.c_double
        self.double_ptr  = ctypes.POINTER(ctypes.c_double)
        self.bool_type   = ctypes.c_bool
        self.char_type   = ctypes.c_char_p
        
        
    
    
    def propagator_c(self,):
        self.orbit_param = OrbitalParameters
        
        lib.propagate.argtypes = [
            self.int_type,
            self.double_type,
            self.int_type,
            ctypes.POINTER(OrbitalParameters),
            self.int_type
        ]
        
        lib.propagate.restype = ctypes.POINTER(Output)
        lib.free_output.argtypes = [ctypes.POINTER(Output)]
        
        return lib
    
    
    def referenceSystem(self,):
        
        lib_projection.currentJulianDateTimeJ2000.argtypes = [
            self.char_type
        ]
        
        lib_projection.currentJulianDateTimeJ2000.restype = self.double_type
        
        return lib_projection