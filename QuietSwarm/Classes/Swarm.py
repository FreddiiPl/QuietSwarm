import numpy as np
from .objectTypes import objectTypes
from QuietSwarm.Helpers.Projections import eciToecef, ecefTolla




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
                            config[1],  # sma
                            config[2],  # ecc
                        ]
                    
                    self.orbitParams[sat_idx, :] = params
                    sat_idx += 1
            

  
    
    def propagate(self, n_steps, dt, stride):
        c_propagator = self.types.propagator_c()
        OrbitArrayType = self.types.orbit_param * len(self.orbitParams)
        
        orbit_array = OrbitArrayType(*[
                self.types.orbit_param(*row)
                for row in self.orbitParams
            ])
        

        output_ptr = c_propagator.propagate(n_steps, dt, self.nr_sats, orbit_array, stride)
        
        
        # Transfer output
        dtype = np.dtype([
                    ("x", np.float64),
                    ("y", np.float64),
                    ("z", np.float64),
                ])
        n = stride * self.nr_sats
        output = np.ctypeslib.as_array(output_ptr, shape=(n,)).view(dtype)
    
        c_propagator.free_output(output_ptr)
        
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
    
    
    def eciToAzEl(self,states, observer):
        states_azel   = states.copy()
        observer_ecef = ... 
        
        
        
        
        
        
        