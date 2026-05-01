from .objectTypes import objectTypes


class Swarm:
    def __init__(self,orbital_params):
        self.types = objectTypes()
        self.orbits = orbital_params
    
    
    def propagate(self, n_steps, dt, n_sats):
        c_propagator = self.types.propagator_c()
        c_propagator.propagate(n_steps, dt, n_sats, self.orbits)    