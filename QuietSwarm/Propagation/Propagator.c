#include <stdlib.h>
#include <stdio.h> 
#include <stddef.h>
#include <stdbool.h>
#include "propagator.h"


void free_output(Output *buffer) {
    free(buffer);
}


Output *propagate(int n_steps, double h, int n_sats, OrbitalParameters *orbit){
    /*
    Initialize output
    */
    Output *buffer = malloc(n_steps * n_sats * sizeof(Output));
    if (!buffer) {
    perror("malloc failed");
    exit(EXIT_FAILURE);
    }

    size_t total_bytes = (size_t)n_steps * (size_t)n_sats * sizeof(Output);
    double mb = total_bytes / (1024.0 * 1024.0);
    double gb = mb / 1024.0;

    printf("Output buffer size: %.2f MB (%.3f GB)\n", mb, gb);


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
        free(buffer);
        return NULL;
    }


    /*
    Initialize state
    */
    for (int sat = 0; sat < swarm.n_sats; sat++) {
        swarm.orbitParam[sat] = orbit[sat];
        State initialState = initialize_state(swarm.orbitParam[sat]);
        swarm.state[sat] = initialState;
    }

    /*
    Integrate
    */

    int idx = 0;
    int max = n_steps * n_sats;
    for (int step = 0; step < n_steps; step++) {
        swarm_step(&swarm, h);
        for (int i = 0; i < swarm.n_sats; i++) {
            if (idx >= max) {
                fprintf(stderr, "Buffer overflow\n");
                exit(EXIT_FAILURE);
            }
            buffer[idx++] = (Output){
                step,
                i,
                swarm.state[i].positions.x,
                swarm.state[i].positions.y,
                swarm.state[i].positions.z
            };
    }

    PROGRESS(step + 1, n_steps);
    }
    printf("\n");



    free(swarm.orbitParam);
    free(swarm.state);
    
    return buffer;
}

