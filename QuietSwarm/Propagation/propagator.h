#include <stdio.h> 

#ifndef PROPAGATOR_H
#define PROPAGATOR_H


#include <math.h>

/*
Progress macro
*/
#define PROGRESS(step, total) \
    do { \
        int width = 40; \
        float ratio = (float)(step) / (total); \
        int pos = ratio * width; \
        printf("\r["); \
        for (int i = 0; i < width; i++) \
            printf(i < pos ? "=" : " "); \
        printf("] %3d%%", (int)(ratio * 100)); \
        fflush(stdout); \
    } while(0)


/*
For general numerical application and stability
*/
#define epsilon 1.0e-12
#define epsilon2 (epsilon * epsilon)

/*
Constants definition - unitless versions based on IERS Convention (2010):
https://iers-conventions.obspm.fr/conventions_material.php
*/
#define mu 1.0
#define a 1.0
#define a_normalizer 63781366
#define J2 0.0010826359

#define sigma_mu 2.0070223615090836e-9
#define sigma_a 1.5678560412142945e-8
#define sigma_J2 1.0e-10


typedef struct {
    double x, y, z;
} Vector3 ;

typedef struct {
    double rightAscensionOfAscendingNode;
    double argumentOfPerigee;
    double inclinationAngle;
    double phaseAngles;
    double semiMajorAxis;
    double eccentricity;
} OrbitalParameters;

typedef struct {
    Vector3 positions;
    Vector3 velocities;
    Vector3 accelerations;
} State;

typedef struct {
    double val;
} KineticEnergy;

typedef struct {
    double val;
} PotentialEnergy;


typedef struct {

    KineticEnergy T;
    PotentialEnergy V;
    double total;

} Hamiltonian;

typedef struct {
    int n_sats;
    OrbitalParameters *orbitParam; // be sure to free once its use is over
    State *state; // be sure to free once its use is over
    Hamiltonian *energy; // be sure to free once its use is over

} Swarm;

typedef struct {
    double x, y, z;
    double T,V,H;
} Output;



State initialize_state(OrbitalParameters orbit);
State verlet_kick_drift_single_sat(State current_state, double h);

void HamiltonianEnergy(Swarm *swarm);
void swarm_step(Swarm *swarm, double h);

Output *propagate(int n_steps, double h, int n_sats, OrbitalParameters *orbit, int stride);

#endif