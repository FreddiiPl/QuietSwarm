#include <stdlib.h>
#include <stdio.h> 
#include <stddef.h>
#include <stdbool.h>
#include "propagator.h"



void free_output(Output *buffer) {
    free(buffer);
}


void store_in_buffer(Output *buffer, const Swarm *swarm) {


    for (int i = 0; i < swarm->n_sats; i++) {
            buffer[i] = (Output){
                swarm->state[i].positions.x,
                swarm->state[i].positions.y,
                swarm->state[i].positions.z,

                swarm->energy[i].T.val,
                swarm->energy[i].V.val,
                swarm->energy[i].total
            };
        }

}


void InitializeState(Swarm *swarm, OrbitalParameters *orbit) {

    for (int sat = 0; sat < swarm->n_sats; sat++) {
        swarm->orbitParam[sat] = orbit[sat];
        State initialState = initialize_state(swarm->orbitParam[sat]);
        swarm->state[sat] = initialState;
    }

}


Output *propagate(int n_steps, double h, int n_sats, OrbitalParameters *orbit, int stride){

    
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
    for (int step = 0; step < n_steps; step++) {
        swarm_step(&swarm, h);
        HamiltonianEnergy(&swarm);
        if (step % stride == 0) {
            if (out_idx < n_stride) {
                store_in_buffer(buffer + (out_idx * n_sats), &swarm);
                out_idx++;
            }
        }
        PROGRESS(step + 1, n_steps);
    }
    printf("\n");


    free(swarm.orbitParam);
    free(swarm.state);
    free(swarm.energy);
    
    return buffer;
}



