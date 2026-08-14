#include "propagator.h"

Hamiltonian compute_energy(const State *state)
{
    Hamiltonian H;
    double posx = state->positions.x;
    double posy = state->positions.y;
    double posz = state->positions.z;

    double velx = state->velocities.x;
    double vely = state->velocities.y;
    double velz = state->velocities.z;

    double r  = sqrt(posx*posx + posy*posy + posz*posz);
    double r2 = r*r;

    H.T.val = 0.5 * (velx*velx + vely*vely + velz*velz);
    H.V.val = -(1.0 / (2.0 * r)) * ( 2.0 + J2 / r2 * (1.0 - 3.0 * posz * posz / r2) );
    H.total = H.T.val + H.V.val;
    
    return H;
}