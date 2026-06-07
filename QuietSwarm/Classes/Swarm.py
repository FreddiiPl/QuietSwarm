import numpy as np
from .objectTypes import objectTypes
from QuietSwarm.Helpers.Projections import eciToecef, ecefTolla, llaToEcef
from QuietSwarm.Helpers.wgs84 import EARTH_SEMI_MAJOR_AXIS, EARTH_MU

import matplotlib.pyplot as plt
import matplotlib as mpl

# Default figure settings
mpl.rcParams['axes.linewidth'] = 1.2
mpl.rcParams['xtick.direction'] = "in"
mpl.rcParams['xtick.top'] = True
mpl.rcParams['ytick.direction'] = "in"
mpl.rcParams['ytick.right'] = True
mpl.rcParams['xtick.minor.visible'] = True
mpl.rcParams['ytick.minor.visible'] = True
mpl.rcParams['font.weight'] = "bold"
mpl.rcParams['axes.labelweight'] = "bold"
mpl.rcParams['font.size'] = 12


class Swarm:
    def __init__(self,orbitalFile):
        self.types = objectTypes()

        # To be cleaned up!!
        with open(orbitalFile, "r") as f:
            nr_configurations = sum(1 for line in f) - 1
            self.nr_sats = 0
            self.temp = np.zeros((nr_configurations, 6)) # ghost number 6...
            
            
            f.seek(0)
            next(f)
            for i, row in enumerate(f):
                
                values = [float(x) for x in row.strip().split(",")]
                n_sat     = values[0]
                apoapsis  = values[1]
                periapsis = values[2]
                
                semiMajorAxis = (apoapsis + periapsis) / 2
                semiMajorAxis += EARTH_SEMI_MAJOR_AXIS / 1e3
                eccentricity  = (apoapsis - periapsis) / (apoapsis + periapsis)
  
                values[1] = semiMajorAxis
                values[2] = eccentricity
                
                self.nr_sats += int(n_sat)
                self.temp[i, :] = values
            
            
            self.orbitParams = np.zeros((self.nr_sats, 6))
            sat_idx = 0
            for config in self.temp:
                n_sat = int(config[0])
                phases = np.linspace(0, 360, n_sat, endpoint=False)
                
                raan_rad = np.deg2rad(config[3])
                argp_rad = np.deg2rad(config[4])
                incl_rad = np.deg2rad(config[5])
                phases_rad = np.deg2rad(phases)
                for k in range(n_sat):
                    params = [
                            raan_rad,  # raan
                            argp_rad,  # argp
                            incl_rad,   # inc
                            phases_rad[k],  # phase
                            config[1] * 1e3,  # sma
                            config[2],  # ecc
                        ]
                    
                    self.orbitParams[sat_idx, :] = params
                    sat_idx += 1
            

  
    
    def propagate(self, tmax, dt):
        c_propagator = self.types.propagator_c()
        OrbitArrayType = self.types.orbit_param * len(self.orbitParams)
        
        orbit_array = OrbitArrayType(*[
                self.types.orbit_param(*row)
                for row in self.orbitParams
            ])
        
        tau        = np.sqrt(EARTH_SEMI_MAJOR_AXIS**3 / EARTH_MU)
        h_norm     = dt / tau
        tmax_norm  = tmax / tau
        n_steps    = int(tmax_norm // h_norm)
        
        stride     = int(1.0 // dt) 
        if stride < 1: stride = 1
        
        
        output_ptr = c_propagator.propagate(n_steps, h_norm, self.nr_sats, orbit_array, stride)
        
        
        # Transfer output
        dtype = np.dtype([
                    ("x", np.float64),
                    ("y", np.float64),
                    ("z", np.float64),
                    ("T", np.float64),
                    ("V", np.float64),
                    ("H", np.float64),
                ])
        n_stride = (n_steps + stride - 1) // stride
        n = n_stride * self.nr_sats
        
        output = np.ctypeslib.as_array(output_ptr, shape=(n,)).view(dtype).copy()

        a_normalizer = EARTH_SEMI_MAJOR_AXIS
        output['x'] *= a_normalizer
        output['y'] *= a_normalizer
        output['z'] *= a_normalizer

        c_propagator.free_output(output_ptr)
        
        print("\n--- PYTHON SIDE DEBUG ---")
        print("Första punkten i Python:", output[0])
        print("Sista punkten i Python: ", output[-1])
        print("-------------------------\n")
        
        return output
        
    
    def eciToecef(self,UT1_time, state_eci):
        '''
        Based on IERS conventions -> GCRS - ITRF conversion using implemented precession-nutation model (IAU2000/2006)
        '''
        
        refsystem      = self.types.julianDate()
        UT1_encoded    = UT1_time.encode('utf-8')
        
        JD             = refsystem.currentJulianDateTime(UT1_encoded)
        absolute_JD = (JD / 86400.0)
        
        self.states_ecef = eciToecef(absolute_JD, state_eci)
        
        return self.states_ecef
        
        
        
    def eciTolla(self,states, **ut1_str):
        states_ecef = states.copy()
        if not hasattr(self, 'states_ecef'):
            try:
                UT1_time = ut1_str.pop("UT1")
            except KeyError as e:
                print(f"missing Universal Time string! {e.message}")
            
            states_ecef = self.eciToecef(UT1_time, states)
        
        
        states_lla = ecefTolla(states_ecef)
        
        return states_lla
    
    
    def ecefToAzEl(self,states, observer: tuple):
 
        latitude_rad   = np.deg2rad(observer[1])
        longitude_rad  = np.deg2rad(observer[0])
        altitude_m     = observer[2]
        
        observer_ecef  = llaToEcef(latitude_rad, longitude_rad, altitude_m)
        
    
        diffx = states['x'] - observer_ecef['x']
        diffy = states['y'] - observer_ecef['y']
        diffz = states['z'] - observer_ecef['z']
        
        # observer local horizon plane
        e     = np.cos(longitude_rad) * diffy - np.sin(longitude_rad) * diffx
        
        n     = - np.sin(latitude_rad) * np.cos(longitude_rad) * diffx \
                - np.sin(latitude_rad) * np.sin(longitude_rad) * diffy \
                + np.cos(latitude_rad) * diffz
        
        u     = np.cos(latitude_rad) * np.cos(longitude_rad) * diffx \
                + np.cos(latitude_rad) * np.sin(longitude_rad) * diffy \
                + np.sin(latitude_rad) * diffz
        
        
        az    = np.rad2deg(np.arctan2(e, n))
        el    = np.rad2deg(np.arcsin(u / np.sqrt(e**2 + n**2 + u**2)))
        
        azel_dtype = np.dtype([('az', '<f8'), ('el', '<f8')])
        result = np.zeros(az.shape, dtype=azel_dtype)
        
        result['az'] = az
        result['el'] = el
        
        return result

    def obstruction(self, states, observer: tuple, elevation_map: np.ndarray):
        # calculate path of satellite through elevation map and determine if it is obstructed
        # almost ray tracing.
        
        
        pass

        
        
        
        
        
        
        
        
        
        
        
        