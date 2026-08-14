import numpy as np
import ctypes
import os
from QuietSwarm.Helpers.Projections import eciToecef, ecefTolla, llaToEcef
from QuietSwarm.Helpers.wgs84 import EARTH_SEMI_MAJOR_AXIS, EARTH_MU

from astropy.time import Time, TimeDelta
from datetime import datetime


base_path = os.path.dirname(__file__)
so_path = os.path.join(base_path,'..','Propagation', 'propagate.so')
lib = ctypes.CDLL(so_path)


class OrbitalParameters(ctypes.Structure):
            _fields_ = [
                ('sat_id', ctypes.c_double),
                ("rightAscensionOfAscendingNode", ctypes.c_double),
                ("argumentOfPerigee", ctypes.c_double),
                ("inclinationAngle", ctypes.c_double),
                ("phaseAngles", ctypes.c_double),
                ("semiMajorAxis", ctypes.c_double),
                ("eccentricity", ctypes.c_double),
            ]


class Output(ctypes.Structure):
    _fields_ = [
        ("sat_id", ctypes.c_double),
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("z", ctypes.c_double),
        ("T", ctypes.c_double),
        ("V", ctypes.c_double),  
        ("H", ctypes.c_double),
    ]


class Swarm:
    '''
    Params -> orbital parameters as input argument.
        Should contain 7 arrays - each of size nr_sats:
            - sat_id
            - raan
            - argp
            - incl_rad
            - phases_rad
            - sma
            - ecc
    '''
    
    def __init__(self,
                 params=None):
        self.orbit_param = OrbitalParameters
        
        self.propagator_argtypes = [
            ctypes.c_int,
            ctypes.c_double,
            ctypes.c_int,
            ctypes.POINTER(OrbitalParameters),
            ctypes.c_int,
            ctypes.c_int
        ]
        
        self.lib = lib
        self.lib.propagate.argtypes = self.propagator_argtypes
        self.lib.propagate.restype = ctypes.POINTER(Output)
        self.lib.free_output.argtypes = [ctypes.POINTER(Output)]
        
        if params is not None:
            self.nr_sats     = params.shape[0]
            self.orbitParams = params
        
   

    def propagate(self, tmax, dt, nr_threads=1, utc=np.datetime64(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "ms")):
        
        utc = Time(utc, scale="utc")
        ut1 = utc.ut1
        
        # c_propagator = self.types.propagator_c()
        
        
        OrbitArrayType = self.orbit_param * len(self.orbitParams)
        
        orbit_array = OrbitArrayType(*[
                self.orbit_param(*row)
                for row in self.orbitParams
            ])
        
        tau        = np.sqrt(EARTH_SEMI_MAJOR_AXIS**3 / EARTH_MU)
        h_norm     = dt / tau
        tmax_norm  = tmax / tau
        n_steps    = int(tmax_norm // h_norm)
        
        stride     = int(1.0 // dt) 
        if stride < 1: stride = 1
        
        output_ptr = self.lib.propagate(n_steps, h_norm, self.nr_sats, orbit_array, stride, nr_threads)
        
        print("sizeof(Output ctypes):", ctypes.sizeof(Output))
        
        # Transfer output
        c_dtype = np.dtype([
                    ("sat_id", np.float64),
                    ("x", np.float64),
                    ("y", np.float64),
                    ("z", np.float64),
                    ("T", np.float64),
                    ("V", np.float64),
                    ("H", np.float64),
                ])
        n_stride = (n_steps + stride - 1) // stride
        n = n_stride * self.nr_sats
        
        raw = np.ctypeslib.as_array(output_ptr, shape=(n,)).view(c_dtype).copy()
    
        
        a_normalizer = EARTH_SEMI_MAJOR_AXIS
        raw['x'] *= a_normalizer
        raw['y'] *= a_normalizer
        raw['z'] *= a_normalizer
        
        energy_normalizer = EARTH_MU / EARTH_SEMI_MAJOR_AXIS
        raw['T'] *= energy_normalizer
        raw['V'] *= energy_normalizer
        raw['H'] *= energy_normalizer
        self.lib.free_output(output_ptr)
        
        
        time_offsets = np.arange(n_stride) * (dt * stride)
        step_ut1 = ut1 + TimeDelta(time_offsets, format='sec')
        times = step_ut1.utc.datetime64.astype("datetime64[ms]")
        
        dtype = np.dtype([
            ("t", np.int64),
            ("sat_id", np.float64),
            ("x", np.float64),
            ("y", np.float64),
            ("z", np.float64),
            ("T", np.float64),
            ("V", np.float64),
            ("H", np.float64),
        ])
        
        output = np.empty(len(raw), dtype=dtype)
        output['t'] = np.repeat(
                                times.astype("datetime64[ms]").astype(np.int64), 
                                self.nr_sats)
        
        output["sat_id"] = raw["sat_id"]
        output['x'] = raw['x']
        output['y'] = raw['y']
        output['z'] = raw['z']
        output['T'] = raw['T']
        output['V'] = raw['V']
        output['H'] = raw['H']

        
        print("\n--- PYTHON SIDE DEBUG ---")
        print("Första punkten i Python:", output[0])
        print("Sista punkten i Python: ", output[-1])
        print("-------------------------\n")
        
        return output
        
    
    def eciToecef(self, state_eci):
        '''
        Based on IERS conventions -> GCRS - ITRF conversion using implemented precession-nutation model (IAU2000/2006)
        '''
        dt64 = state_eci["t"].astype("datetime64[ms]")
        
        utc = Time(
            dt64,
            format="datetime64",
            scale="utc"
        )

        
        ecef_dtype = np.dtype([
                    ("t", np.int64),
                    ("sat_id", np.float64),
                    ("x", np.float64),
                    ("y", np.float64),
                    ("z", np.float64),
                    ("T", np.float64),
                    ("V", np.float64),
                    ("H", np.float64),
                    ])
                
        
        ecef = eciToecef(utc, state_eci)
        states_ecef = np.empty(len(state_eci), dtype=ecef_dtype)
        
        states_ecef["t"] = state_eci["t"]
        states_ecef["sat_id"] = state_eci["sat_id"]
        states_ecef["x"] = ecef["x"]
        states_ecef["y"] = ecef["y"]
        states_ecef["z"] = ecef["z"]
        states_ecef["T"] = state_eci["T"]
        states_ecef["V"] = state_eci["V"]
        states_ecef["H"] = state_eci["H"]
        
        return states_ecef
        
        
        
    def eciTolla(self,states):
        states_ecef = states.copy()
        if not hasattr(self, 'states_ecef'):
            
            states_ecef = self.eciToecef(states)
        
        lla_dtype = np.dtype([
            ("t", np.int64),
            ("sat_id", np.float64),
            ("longitude", np.float64),
            ("latitude", np.float64),
            ("altitude", np.float64),
            ("T", np.float64),
            ("V", np.float64),
            ("H", np.float64),
            ])
        
        
        lla = ecefTolla(states_ecef)
        states_lla = np.empty(len(states_ecef), dtype=lla_dtype)
        
        states_lla["t"] = states["t"]
        states_lla["longitude"] = lla["longitude"]
        states_lla["latitude"]  = lla["latitude"]
        states_lla["altitude"]  = lla["altitude"]
        states_lla["T"] = states["T"]
        states_lla["V"] = states["V"]
        states_lla["H"] = states["H"]
        
        return states_lla
    
    
    def ecefToAzEl(self,states, observer: tuple):
 
        latitude_rad   = np.deg2rad(observer[1])
        longitude_rad  = np.deg2rad(observer[0])
        altitude_m     = observer[2]
        
        observer_ecef  = llaToEcef(latitude_rad, longitude_rad, altitude_m)
        

        diffx = states['x'] - observer_ecef['x']
        diffy = states['y'] - observer_ecef['y']
        diffz = states['z'] - observer_ecef['z']
        dist  = np.sqrt(diffx**2 + diffy**2 + diffz**2)
        
        diffx_unit = diffx / dist
        diffy_unit = diffy / dist
        diffz_unit = diffz / dist
        
        # observer local horizon plane
        e     = -np.cos(longitude_rad) * diffy_unit + np.sin(longitude_rad) * diffx_unit
        
        n     = - np.sin(latitude_rad) * np.cos(longitude_rad) * diffx_unit \
                - np.sin(latitude_rad) * np.sin(longitude_rad) * diffy_unit \
                + np.cos(latitude_rad) * diffz_unit
        
        u     = np.cos(latitude_rad) * np.cos(longitude_rad) * diffx_unit \
                + np.cos(latitude_rad) * np.sin(longitude_rad) * diffy_unit \
                + np.sin(latitude_rad) * diffz_unit
        
        
        az    = np.rad2deg(np.arctan2(e, n))
        el    = np.rad2deg(np.arcsin(u / np.sqrt(e**2 + n**2 + u**2)))
        
        azel_dtype = np.dtype([('az', '<f8'), ('el', '<f8'), ('distance', '<f8')])
        result = np.zeros(az.shape, dtype=azel_dtype)
        
        result['az']       = az
        result['el']       = el
        result['distance'] = dist
        
        return result


    def obstruction(self, states, observer):
        # calculate path of satellite through elevation map and determine if it is obstructed
        # ray marching
        
        raise NotImplementedError("Not implemented yet")
    
    

        
        