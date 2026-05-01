#include "propagator.h"


void propagate (int n_steps, double h, int n_sats, OrbitalParameters orbit){
    /*
    initialize Swarm
    */
   Swarm swarm;
   swarm.n_sats     = n_sats;
   swarm.orbitParam = malloc(sizeof(OrbitalParameters) * swarm.n_sats);
   swarm.state      = malloc(sizeof(State) * swarm.n_sats);

    if (!swarm.orbitParam || !swarm.state) {
        free(swarm.orbitParam);
        free(swarm.state);
        return;
    }


    /*
    Initialize state
    */
    for (int sat = 0; sat < swarm.n_sats; sat++) {
        swarm.orbitParam[sat] = orbit;
        State initialState = initialize_state(swarm.orbitParam[sat]);
        swarm.state[sat] = initialState;
    }


    /*
    Integrate
    */
   for (int step = 0; step < n_steps; step++) {
        swarm_step(&swarm, h);
   }


   free(swarm.orbitParam);
   free(swarm.state);
}
