#include "propagator.h"

void HamiltonianEnergy(Swarm *swarm) {
    
    
    KineticEnergy T;
    PotentialEnergy V;
    
    double posx, posy, posz, r, r2;
    double velx, vely, velz;
    for (int sat=0; sat < swarm->n_sats; sat++) { 
        posx = swarm->state[sat].positions.x;
        posy = swarm->state[sat].positions.y;
        posz = swarm->state[sat].positions.z;
        r = sqrt(posx*posx + posy*posy + posz * posz);
        r2 = r * r;

        velx = swarm->state[sat].velocities.x;
        vely = swarm->state[sat].velocities.y;
        velz = swarm->state[sat].velocities.z;

        T.val = 0.5 * (velx*velx + vely*vely + velz*velz);
        V.val = (1.0 / (2.0 * r)) * ( 2 - J2 / r2 * (3 * posz * posz / r2 - 1) );  

        swarm->energy[sat].T = T;
        swarm->energy[sat].V = V;
        swarm->energy[sat].total = T.val + V.val;
    }
}