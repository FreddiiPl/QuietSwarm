#include <stdlib.h>
#include <stdio.h> 
#include <stddef.h>
#include <stdbool.h>
#include "propagator.h"


void propagate(int n_steps, double h, int n_sats, OrbitalParameters *orbit, bool debug){
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
       swarm.orbitParam[sat] = orbit[sat];
       State initialState = initialize_state(swarm.orbitParam[sat]);
       swarm.state[sat] = initialState;
    }
    
    if (debug) {
        size_t orbit_mem = sizeof(OrbitalParameters) * swarm.n_sats;
        size_t state_mem = sizeof(State) * swarm.n_sats;
 
        printf("\n=== Swarm Memory Allocation ===\n");
 
        printf("Satellite: %d\n", swarm.n_sats);
        printf("a: ");
        for (int i = 0; i < swarm.n_sats; i++) {
            printf("%8.2f ", swarm.orbitParam[i].semiMajorAxis);

            if ((i + 1) % 10 == 0)
                printf("\n");
        }
        printf("\n");
 
        printf("e: ");
        for (int i = 0; i < swarm.n_sats; i++) {
            printf("%8.2f ", swarm.orbitParam[i].eccentricity);

            if ((i + 1) % 10 == 0)
                printf("\n");
        }
        printf("\n");
 
        printf("i: ");
        for (int i = 0; i < swarm.n_sats; i++) {
            printf("%8.2f ", swarm.orbitParam[i].inclinationAngle);

            if ((i + 1) % 10 == 0)
                printf("\n");
        }
        printf("\n");

        printf("M: ");
        for (int i = 0; i < swarm.n_sats; i++) {
            printf("%8.2f ", swarm.orbitParam[i].phaseAngles);

            if ((i + 1) % 10 == 0)
                printf("\n");
        }
        printf("\n");
 
 
        printf("\nOrbital Parameters\n");
        printf("  Struct size       : %zu bytes\n", sizeof(OrbitalParameters));
        printf("  Total allocation  : %zu bytes\n", orbit_mem);
 
        printf("\nState Vectors\n");
        printf("  Struct size       : %zu bytes\n", sizeof(State));
        printf("  Total allocation  : %zu bytes\n", state_mem);
 
        printf("\nTotal Memory        : %zu bytes\n", orbit_mem + state_mem);
 
        printf("================================\n\n");
    }

    /*
    Integrate
    */
   
   for (int step = 0; step < n_steps; step++) {
        swarm_step(&swarm, h);
        PROGRESS(step + 1, n_steps);
   }
   printf("\n");


   free(swarm.orbitParam);
   free(swarm.state);
}
