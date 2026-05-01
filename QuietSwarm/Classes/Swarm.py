import numpy as np
from .objectTypes import objectTypes


class Swarm:
    def __init__(self,orbitalFile):
        self.types = objectTypes()
        
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
                
                for k in range(n_sat):
                    params = [
                            config[3],  # raan
                            config[4],  # argp
                            config[5],  # inc
                            phases[k],  # phase
                            config[1],  # sma
                            config[2],  # ecc
                        ]
                    
                    self.orbitParams[sat_idx, :] = params
                    sat_idx += 1
            
                
        
            
            
    
    def propagate(self, n_steps, dt):
        c_propagator = self.types.propagator_c()
        OrbitArrayType = self.types.orbit_param * len(self.orbitParams)
        
        orbit_array = OrbitArrayType(*[
                self.types.orbit_param(*row)
                for row in self.orbitParams
            ])
        
        
        c_propagator.propagate(n_steps, dt, self.nr_sats, orbit_array, True)