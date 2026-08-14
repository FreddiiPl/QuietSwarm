#include <stdlib.h>
#include <stdio.h> 
#include <stddef.h>
#include <stdbool.h>
#include <omp.h>
#include "propagator.h"



void free_output(Output *buffer) {
    free(buffer);
}


void InitializeState(Swarm *swarm, OrbitalParameters *orbit) {

    for (int sat = 0; sat < swarm->n_sats; sat++) {
        swarm->orbitParam[sat] = orbit[sat];
        State initialState = initialize_state(swarm->orbitParam[sat]);
        swarm->state[sat] = initialState;
    }

}

Output *propagate(int n_steps, double h, int n_sats, OrbitalParameters *orbit, int stride,
                  int nr_threads){

    
    int n_stride = (n_steps + stride - 1) / stride;
    Output *buffer = malloc((size_t)n_stride * n_sats * sizeof(Output));
    if (!buffer) {
    perror("malloc failed");
    exit(EXIT_FAILURE);
    }

    size_t total_bytes = (size_t) n_stride * n_sats * sizeof(Output);
    double mb = total_bytes / (1024.0 * 1024.0);
    double gb = mb / 1024.0;

    printf("Output buffer size: %.2f MB (%.3f GB)\n", mb, gb);


    Swarm swarm;
    swarm.n_sats     = n_sats;
    swarm.orbitParam = malloc(sizeof(OrbitalParameters) * swarm.n_sats);
    swarm.state      = malloc(sizeof(State) * swarm.n_sats);
    swarm.energy     = malloc(sizeof(Hamiltonian) * swarm.n_sats);
    if (!swarm.orbitParam || !swarm.state || !swarm.energy) {
        free(swarm.orbitParam);
        free(swarm.state);
        free(swarm.energy);
        free(buffer);
        return NULL;
    }

    InitializeState(&swarm, orbit);

    int out_idx = 0;
    int actual_threads = (nr_threads > 0) ? nr_threads : omp_get_max_threads();
    #pragma omp parallel for num_threads(actual_threads) schedule(static)
    for (int sat=0; sat < n_sats; sat++) {
        State state = swarm.state[sat];

        for (int step = 0; step < n_steps; step++) {
            state  = verlet_kick_drift_single_sat(state, h);
            
            if (step % stride == 0) {
                
                Hamiltonian H = compute_energy(&state);
                
                int sample = step / stride;

                buffer[sample * n_sats + sat] = (Output){
                    swarm.orbitParam[sat].sat_id,
                    state.positions.x,
                    state.positions.y,
                    state.positions.z,
                    H.T.val,
                    H.V.val,
                    H.total
                };
            }

        }
        swarm.state[sat] = state;
    }

    free(swarm.orbitParam);
    free(swarm.state);
    free(swarm.energy);
    
    return buffer;
}



