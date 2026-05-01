import numpy as np
# from .objectTypes import objectTypes


class Swarm:
    def __init__(self,orbitalFile):
        # self.types = objectTypes()
        
        with open(orbitalFile, "r") as f:
            nr_configurations = sum(1 for line in f) - 1
            self.orbitParams = np.zeros((nr_configurations, 7)) # ghost number 7...
            
            f.seek(0)
            next(f)
            for i, row in enumerate(f):
                values = [float(x) for x in row.strip().split(",")]
                
                self.orbitParams[i, :] = values
        
        
        print(self.orbitParams)  
                
                
            
            
            
    
    
    def propagate(self, n_steps, dt, n_sats):
        c_propagator = self.types.propagator_c()
        c_propagator.propagate(n_steps, dt, n_sats, self.orbits, debug=True)