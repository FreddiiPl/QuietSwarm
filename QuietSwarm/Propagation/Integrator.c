
#include <math.h>
#include <stdio.h>
#include "propagator.h"
#include "utils.h"


State verlet_kick_drift_single_sat(State current_state, double h) {
    double h2 = 0.5 * h;

    State next_state;

    Vector3 halfVelocity;
    Vector3 currentPos = current_state.positions;
    Vector3 currentVel = current_state.velocities;
    Vector3 currentAcc = current_state.accelerations;

    Vector3 nextPos;
    Vector3 nextVel;
    Vector3 nextAcc;
    
    double r_squared = currentPos.x * currentPos.x + currentPos.y * currentPos.y + currentPos.z * currentPos.z;

    halfVelocity.x = compute_velocity(currentVel.x, currentAcc.x, h2);
    halfVelocity.y = compute_velocity(currentVel.y, currentAcc.y, h2);
    halfVelocity.z = compute_velocity(currentVel.z, currentAcc.z, h2);

    nextPos.x = h * halfVelocity.x;
    nextPos.y = h * halfVelocity.y;
    nextPos.z = h * halfVelocity.z;

    double r_squared_next = nextPos.x * nextPos.x + nextPos.y * nextPos.y + nextPos.z * nextPos.z;

    nextAcc.x = compute_acceleration(nextPos.x, nextPos.z, r_squared_next, 0);
    nextAcc.y = compute_acceleration(nextPos.y, nextPos.z, r_squared_next, 1);
    nextAcc.z = compute_acceleration(nextPos.z, nextPos.z, r_squared_next, 2);

    nextVel.x = compute_velocity(halfVelocity.x, nextAcc.x, h2);
    nextVel.y = compute_velocity(halfVelocity.y, nextAcc.y, h2);
    nextVel.z = compute_velocity(halfVelocity.z, nextAcc.z, h2);

    next_state.positions     = nextPos;
    next_state.velocities    = nextVel;
    next_state.accelerations = nextAcc;

    return next_state;
}


void swarm_step(Swarm *swarm, double h) {
    int n_sats = swarm -> n_sats;

    for (int sat = 0; sat < n_sats; sat++) {
        State *current_state = &swarm -> state[sat];

        State next_state = verlet_kick_drift_single_sat(*current_state, h);

        swarm->state[sat] = next_state;
    }
}