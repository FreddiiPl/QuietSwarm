#include <stddef.h>
#include <stdbool.h>
#include "propagator.h"


void propagate (int n_steps, double h, int n_sats, OrbitalParameters orbit, bool debug){
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

    if (debug) {
        size_t orbit_mem = sizeof(OrbitalParameters) * swarm.n_sats;
        size_t state_mem = sizeof(State) * swarm.n_sats;

        printf("Allocated orbitParam: %zu bytes (%zu each × %d)\n",
           orbit_mem,
           sizeof(OrbitalParameters),
           swarm.n_sats);

        
        printf("Allocated state: %zu bytes (%zu each × %d)\n",
           state_mem,
           sizeof(State),
           swarm.n_sats);

        printf("Total allocated: %zu bytes\n",
                orbit_mem + state_mem);
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
